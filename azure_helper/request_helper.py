def create_request_header(cached_access_token: str) -> str:
    """
    Creates a request header to pass to the API call
    """
    # build the request header dictionary
    request_header = {
        "Authorization": f"Bearer {cached_access_token}",
        "Content-Type": "application/json",
    }
    return request_header


def create_request_body(
    target_subscription_id: str, target_resource_group: str, resource_ids: str
) -> str:
    """
    Creates a request body to pass to the API
    """
    # pylint: disable=line-too-long
    target_resource_group = str(
        f"/subscriptions/{target_subscription_id}/resourceGroups/{target_resource_group}"
    )
    request_body = str(
        {"resources": resource_ids, "targetResourceGroup": target_resource_group}
    ).replace("'", '"')
    return request_body
