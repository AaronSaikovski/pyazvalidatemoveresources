import requests
import time

import utils.console_helper as console_helper
import common.constants as constants


def call_validate_api(
    source_subscription_id: str, source_resource_group: str, request_header: str, request_body: str
) -> requests.Response:
    '''
    Calls the validateMoveResources to check if the resources can be moved.
    Ref: https://learn.microsoft.com/en-us/rest/api/resources/resources/validate-move-resources
    '''
    # Build the API and call it and get the response code
    # pylint: disable=line-too-long
    validate_move_api = str(
        f"https://management.azure.com/subscriptions/{source_subscription_id}/resourceGroups/{source_resource_group}/validateMoveResources?api-version=2021-04-01"
    )

    # Call the API - Using requests library
    api_response = requests.post(
        url=validate_move_api, data=request_body, headers=request_header, timeout=constants.API_TIMEOUT
    )
    return api_response


def call_management_api(source_api_response: requests.Response, request_header: str) -> str:
    '''
    Calls the Validation Management API URI from the raw initial payload

    Perform the validation of resource move against the Management API
    Return codes:
        Success == HTTP response code 204 (no content)
        Error == HTTP response code 409 (Conflict)
    '''
    # Get the Validation management URI from the raw content string payload
    check_uri: str
    validate_api_status_code: requests.Response = constants.API_SUCCESS
    validate_api_response_data: requests.Response

    # Main API - Status code success - 202
    if source_api_response.status_code == constants.API_SUCCESS:
        # Get the response header info
        api_response_headers = source_api_response.headers

        # Get the Location from the response header
        check_uri = api_response_headers['Location']

        # do the loop until we aren't receiving a 202 return code back
        # API doesnt get called the first time around due to throttling/the API not being called
        while validate_api_status_code == 202:
            # Call the Management API from the Location header value from the validation API call
            management_api = requests.get(url=check_uri, headers=request_header, timeout=constants.API_TIMEOUT)

            # Get the response code
            validate_api_status_code = management_api.status_code
            console_helper.print_confirmation_message("Processing....")

            # Get the response data back from the API call
            validate_api_response_data = management_api.content

            # Sleep for 3 seconds to stop API request flooding
            time.sleep(3)

        # Report status back
        # 204 - Success resources can be moved
        if validate_api_status_code == constants.API_RESOURCE_MOVE_OK:
            console_helper.print_ok_message("**SUCCESS CODE = 204 - NO ISSUES FOUND**")
        # 409 - resources cannot be moved
        elif validate_api_status_code == constants.API_RESOURCE_MOVE_FAIL:
            console_helper.print_error_message("**ERROR CODE = 409 - ISSUES FOUND**")
            console_helper.print_error_message(f"Detailed Error Data: {validate_api_response_data}")
        # Some other error
        else:
            console_helper.print_error_message("**UNKNOWN ERROR**")
