import os
import re
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain関連のインポート
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from langchain.tools import Tool
from langchain.tools.retriever import create_retriever_tool
from langchain_google_community import GoogleSearchAPIWrapper
from langchain.agents import initialize_agent, AgentType

# HANA関連のインポート
from langchain_hana import HanaInternalEmbeddings
from langchain_hana import HanaDB
from hdbcli import dbapi

# 環境変数を読み込む
load_dotenv(verbose=True)

# FastAPIアプリケーションを初期化
app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# リクエストモデル
class QueryRequest(BaseModel):
    query: str

# ChatOpenAIを初期化
chat_llm = ChatOpenAI(deployment_id=os.getenv("DEVELOPMENT_ID"))

# Google検索ツールを設定
search = GoogleSearchAPIWrapper(k=5)
google_tool = Tool.from_function(
    name="google_search",
    description="Search Google and return the first results",
    func=search.run
)

# embeddingsを初期化
embeddings = HanaInternalEmbeddings(
    internal_embedding_model_id="SAP_NEB.20240715"
)

# HANA Cloudと接続
connection = dbapi.connect(
    address=os.getenv("HANA_DB_ADDRESS"),
    port=os.getenv("HANA_DB_PORT"),
    user=os.getenv("HANA_DB_USER"),
    password=os.getenv("HANA_DB_PASSWORD"),
    sslValidateCertificate=False,
    autocommit=True,
)

# データベースの立ち上げ
db = HanaDB(
    embedding=embeddings,
    connection=connection,
    table_name="TEST_TABLE"
)

# retrieverツールを設定
retriever_tool = create_retriever_tool(
    retriever=db.as_retriever(),
    name="hana_vectorengine",
    description=(
        "Use this tool to search internal SAP documents stored "
        "in HANA Cloud Vector Engine when the user asks company-specific questions."
    ),
)

# エージェントを初期化
agent = initialize_agent(
    tools=[google_tool, retriever_tool],
    llm=chat_llm,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    return_intermediate_steps=True,
)

def extract_thought_from_log(log):
    if not log or not isinstance(log, str):
        return ""

    # 文字列のパターンを定義
    patterns = [
        # 英語
        r'Thought:\s*(.*?)(?:\nAction:|$)',
        r'^(.*?)(?:\nAction:|$)',

        r'思考:\s*(.*?)(?:\nアクション:|$)',
        r'^(.*?)(?:\nアクション:|$)'
    ]

    for pattern in patterns:
        match = re.search(pattern, log, re.DOTALL | re.IGNORECASE)
        if match:
            thought = match.group(1).strip()
            # 空文字列や改行のみの場合はスキップ
            if thought and not thought.isspace():
                return thought

    # マッチしない場合は元のログを返す
    return log.strip()

def transform_response(raw_response):
    if not isinstance(raw_response, dict):
        return {"output": "", "intermediate_steps": []}

    output = raw_response.get('output', '')
    intermediate_steps = raw_response.get('intermediate_steps', [])

    if not isinstance(intermediate_steps, list):
        intermediate_steps = []

    structured_steps = []

    for idx, step in enumerate(intermediate_steps, 1):
        try:
            # ステップが辞書形式の場合（既に構造化されている場合）
            if isinstance(step, dict):
                structured_steps.append(step)
                continue

            # ステップがタプル形式の場合
            if isinstance(step, tuple) and len(step) == 2:
                action, observation = step

                # ログからThoughtを抽出
                thought = ""
                if hasattr(action, 'log') and action.log:
                    thought = extract_thought_from_log(action.log)

                # 構造化されたステップを作成
                structured_step = {
                    "step_no": idx,
                    "Thought": thought,
                    "action": getattr(action, 'tool', 'unknown'),
                    "action_input": getattr(action, 'tool_input', {}),
                    "Observation": observation if observation is not None else ""
                }
                structured_steps.append(structured_step)

        except Exception:
            # エラーが発生した場合はスキップ
            continue

    return {
        "output": output,
        "intermediate_steps": structured_steps
    }

@app.post("/agent/chat")
async def chat(request: QueryRequest):
    """エージェントにクエリを実行し、構造化されたレスポンスを返す"""
    # エージェントを実行
    raw_response = agent.invoke({"input": request.query})

    # レスポンスを変換
    structured_response = transform_response(raw_response)

    return structured_response

@app.post("/agent/upload")
async def upload_file(file: UploadFile = File(...)):
    """テキストファイルをアップロードしてHANAに埋め込みデータとして格納"""
    
    # ファイル形式のチェック
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=400,
            detail="txt形式のファイルのみアップロード可能です。"
        )
    
    try:
        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_file_path = tmp_file.name
        
        # テキストファイルを読み込み
        text_documents = TextLoader(
            tmp_file_path
        ).load()
        
        # テキストを適切なチャンクに分割
        text_splitter = CharacterTextSplitter(
            chunk_size = 50,
            chunk_overlap = 0,
        )
        
        text_chunks = text_splitter.split_documents(text_documents)
        
        # HANAベクターデータベースに格納
        db.add_documents(text_chunks)
        
        # 一時ファイルを削除
        os.unlink(tmp_file_path)
        
        return UploadResponse(
            message="ファイルが正常にアップロードされ、埋め込み処理が完了しました。",
            filename=file.filename,
            chunks_created=len(text_chunks)
        )
        
    except Exception as e:        
        raise HTTPException(
            status_code=500,
            detail=f"ファイル処理中にエラーが発生しました: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)