# SAP HANA Cloud を用いたチャットボット

このプロジェクトは、Streamlit を使用して構築されたチャットボットアプリケーションで、インタラクティブな会話機能を提供します。
以下には、セットアップ、実行、およびこのプロジェクトに貢献する方法の詳細が記載されています。

## プロジェクト概要

このプロジェクトでは、以下の技術およびライブラリを使用しています：
- **Streamlit**: インタラクティブなウェブインターフェースを構築するため。
- **LangChain**: 会話型リトリーバルチェーンの実装。
- **HanaDB**: ベクトルストア機能のため。
- **OpenAI**: 埋め込みおよび言語モデル機能のため。

## 特徴

- 動的スタイルでカスタマイズ可能なチャットインターフェース。
- LangChain を使用した会話型リトリーバルチェーン。
- 埋め込みの保存とリトリーバルのための HanaDB との統合。
- 機密情報のための `.env` ファイルを使用した安全なトークン管理。

## セットアップ

### 前提条件

以下がインストールされていることを確認してください：
- Python 3.8 以上
- pip (Python パッケージインストーラ)

### インストール

1. このリポジトリをクローンします：
    ```bash
    git clone https://github.com/itomondAtWork/streamlit-chatbot.git
    cd streamlit-chatbot
    ```

2. 仮想環境を作成してアクティベートします：
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows の場合は `venv\Scripts\activate`
    ```

3. 必要なパッケージをインストールします：
    ```bash
    pip install -r requirements.txt
    ```

4. プロジェクトのルートディレクトリに `.env` ファイルを作成し、以下の環境変数を追加します：
    ```plaintext
    AICORE_AUTH_URL=https://example.com
    AICORE_CLIENT_ID=your_client_id
    AICORE_CLIENT_SECRET=your_client_secret
    HANA_DB_ADDRESS=your_hana_db_address
    HANA_DB_PORT=your_hana_db_port
    HANA_DB_USER=your_hana_db_user
    HANA_DB_PASSWORD=your_hana_db_password
    EMBEDDING_DEPLOYMENT_ID=your_embedding_deployment_id
    LLM_DEPLOYMENT_ID=your_llm_deployment_id
    ```

## アプリケーションの実行

1. `src` ディレクトリに移動します：
    ```bash
    cd src
    ```

2. Streamlit アプリケーションを開始します：
    ```bash
    streamlit run main.py
    ```

3. ウェブブラウザを開き、`http://localhost:8501` にアクセスしてチャットボットと対話します。

<!---
itomondAtWork/itomondAtWork is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->
