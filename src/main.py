#!/usr/bin/env python
"""
Validates a source Azure resource group and all child resources to check 
for moveability support into a target resource group within a target subscription.

This script takes a Source SubscriptionID and Source ResourceGroup as 
parameters, analyzes the subscription/resource group.
and gathers a list of resource Ids and excludes those 
resources that cannot be moved based on the resource ID list.
"""
import os
import re
import functools
import logging
import time
import requests

from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient

import console_helper


# set logging level
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()

def log(func):
    '''
    Logging decorator
    source: https://ankitbko.github.io/blog/2021/04/logging-in-python/
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        logger.debug("function {%f} called with args {%s}",func.__name__,signature)
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as ex:
            # pylint: disable=logging-fstring-interpolation
            logger.exception(f"Exception raised in {func.__name__}. exception: {str(ex)}")
            raise ex
    return wrapper

@log
def check_valid_subscription_id(subscription_id: str) -> bool:
    '''
    checks for a valid Azure Subscription ID - Format 00000000-0000-0000-0000-000000000000
    '''
    # check if a string
    if isinstance(subscription_id, str):
        # pylint: disable=line-too-long
        # pylint: disable=anomalous-backslash-in-string
        re_result = re.search("^(\{{0,1}([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}\}{0,1})$", subscription_id)
        if re_result:
            return True

@log
def get_resource_client(source_subscription_id: str) -> ResourceManagementClient:
    '''
    Gets the resource client for the current AZ context
    '''
    # Acquire a credential object using CLI-based authentication.
    credential = AzureCliCredential()

    #check for valid subscription ID
    if check_valid_subscription_id(source_subscription_id):
        # Obtain the management object for resources.
        return ResourceManagementClient(credential, source_subscription_id)

@log
def get_az_cached_access_token() -> object:
    '''
    Gets the cached access token from the AZ CLI session token
    '''
    credential = AzureCliCredential()
    access_token = credential.get_token("https://management.azure.com/.default")
    return access_token.token


@log
def get_resource_ids(resource_client: str,
                     source_resource_group: str) -> list[str]:
    '''
    Gets the given resource IDs for a given resource group - returns a JSON str
    '''
    resources =  resource_client.resources.list_by_resource_group(
        source_resource_group, expand = "createdTime,changedTime")

    # get the resource ids as a list
    resource_ids = []
    for resource in resources:
        resource_ids.append(resource.id)
    return resource_ids

@log
def create_request_header(cached_access_token: str) -> str:
    '''
    Creates a request header to pass to the API call
    '''
    # build the request header dictionary
    request_header = {
        "Authorization": f"Bearer {cached_access_token}",
        "Content-Type": "application/json"
    }
    return request_header

@log
def create_request_body(target_subscription_id:str,
                        target_resource_group: str,
                        resource_ids: str) -> str:
    '''
    Creates a request body to pass to the API
    '''
    # pylint: disable=line-too-long
    target_resource_group = str(f"/subscriptions/{target_subscription_id}/resourceGroups/{target_resource_group}")
    request_body = str({"resources":resource_ids,
                        "targetResourceGroup":target_resource_group}).replace("'", '"')
    return request_body

@log
def call_validate_api(source_subscription_id: str,
                      source_resource_group: str,
                      request_header: str,
                      request_body: str) -> requests.Response:
    '''
    Calls the validateMoveResources to check if the resources can be moved.
    Ref: https://learn.microsoft.com/en-us/rest/api/resources/resources/validate-move-resources
    '''
    # Build the API and call it and get the response code
    # pylint: disable=line-too-long
    validate_move_api = str(f"https://management.azure.com/subscriptions/{source_subscription_id}/resourceGroups/{source_resource_group}/validateMoveResources?api-version=2021-04-01")

    # Call the API - Using requests library
    api_response = requests.post(url=validate_move_api,data=request_body,headers=request_header, timeout=20)
    return api_response


@log
def call_management_api(source_api_response: requests.Response,
                        request_header: str) -> str:
    '''
    Calls the Validation Management API URI from the raw initial payload
    
    Perform the validation of resource move against the Management API
    Return codes:
        Success == HTTP response code 204 (no content)
        Error == HTTP response code 409 (Conflict)
    '''
    # Get the Validation management URI from the raw content string payload
    check_uri: str
    validate_api_status_code: requests.Response = 202
    validate_api_response_data: requests.Response

    # Main API - Status code success - 202
    if source_api_response.status_code == 202:

        # Get the response header info
        api_response_headers = source_api_response.headers

        # Get the Location from the response header
        check_uri = api_response_headers['Location']

        # do the loop until we aren't receiving a 202 return code back
        # API doesnt get called the first time around due to throttling/the API not being called
        while validate_api_status_code == 202:

            # Call the Management API from the Location header value from the validation API call
            management_api = requests.get(url=check_uri,headers=request_header, timeout=20)

            # Get the response code
            validate_api_status_code = management_api.status_code
            console_helper.print_confirmation_message(f"Status code is: {validate_api_status_code}")

            #Get the response data back from the API call
            validate_api_response_data = management_api.content

            # Sleep for 3 seconds to stop API request flooding
            time.sleep(3)

        # Report status back
        # 204 - Success resources can be moved
        if validate_api_status_code == 204:
            console_helper.print_ok_message("**SUCCESS CODE 204 - NO ISSUES FOUND**")
        # 409 - resources cannot be moved
        elif validate_api_status_code == 409:
            console_helper.print_error_message("**ERROR CODE 409 - ISSUES FOUND**")
            console_helper.print_error_message(f"Error Data: {validate_api_response_data}")
        # Some other error
        else:
            console_helper.print_error_message("**UNKNOWN ERROR**")


@log
def main() -> None:
    '''
    Main method
    '''
    # take environment variables from .env.
    load_dotenv()

    # Retrieve Azure values from environment variables.
    source_subscription_id = os.getenv("SOURCE_AZURE_SUBSCRIPTION_ID")
    source_resource_group = os.getenv("SOURCE_RESOURCE_GROUP_NAME")
    target_subscription_id = os.getenv("TARGET_AZURE_SUBSCRIPTION_ID")
    target_resource_group = os.getenv("TARGET_RESOURCE_GROUP_NAME")

    console_helper.print_ok_message("***STARTED PROCESSING***")

    # Obtain the management object for resources.
    resource_client = get_resource_client(source_subscription_id)

    # Get the resource IDs
    resource_ids = get_resource_ids(resource_client, source_resource_group)

    # Build the request header - passing in the access token
    request_header = create_request_header(get_az_cached_access_token())

    # Build the body of the request to be passed to the API
    request_body = create_request_body(target_subscription_id,
                                       target_resource_group,
                                       resource_ids)

    # Call the API and get a response code back
    api_response = call_validate_api(source_subscription_id,
                                     source_resource_group,
                                     request_header, request_body)

    # Call the management API
    call_management_api(api_response,request_header)

    console_helper.print_ok_message("***COMPLETED PROCESSING***")

# call main
if __name__ == '__main__':
    main()
    