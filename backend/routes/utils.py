def paginate_results(results, page, per_page, base_url, query_params=None):
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = results[start:end]

    next_url = None
    if end < len(results):
        query_params = query_params or {}
        query_params.update({"page": page + 1, "per_page": per_page})
        query_string = "&".join(
            [f"{key}={value}" for key, value in query_params.items()]
        )
        next_url = f"{base_url}?{query_string}"

    return paginated_results, next_url
 