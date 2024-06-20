def run_similarity_search(db, query):
    results = db.similarity_search_with_score(query, k=100)  # 類似検索の実行
    formatted_results = []
    for rank, (result, score) in enumerate(results, start=1):
        file_name = result.metadata.get('source_filename', 'Unknown')
        formatted_results.append({
            "Rank": rank,
            "Filename": file_name,
            "Score": score,
        })
    return formatted_results
