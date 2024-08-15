""" Utility functions for the routes module. """

from typing import List

from backend.models import Post


def paginate_results(
    results: List[Post],
    page: int,
    per_page: int,
    base_url: str,
    query_params: str = None,
) -> tuple:
    """
    Paginate a list of results.

    Args:
        results (List[Post]): list of results to paginate
        page (int):  page number
        per_page (int): number of results per page
        base_url (str): base url for the pagination links
        query_params (str, optional): query parameters to 
        include in the pagination links. Defaults to None.

    Returns:
        tuple: a tuple containing the paginated results and the next page URL
    """

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
