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
import requests
from dotenv import load_dotenv

from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient


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
        # resource_client = ResourceManagementClient(credential, source_subscription_id)
        # return resource_client
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
                      request_body: str) -> object:
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

    # Obtain the management object for resources.
    resource_client = get_resource_client(source_subscription_id)

    #get the resource IDs
    resource_ids = get_resource_ids(resource_client, source_resource_group)
    #print(resource_ids)

    # build the request header - passing in the access token
    request_header = create_request_header(get_az_cached_access_token())
    #print(request_header)

    #build the body of the request to be passed to the API
    request_body = create_request_body(target_subscription_id,
                                       target_resource_group,
                                       resource_ids)
    #print(request_body)

    #Call the API and get a response code back
    api_response = call_validate_api(source_subscription_id,
                                     source_resource_group,
                                     request_header, request_body)
    print(api_response)

# call main
if __name__ == '__main__':
    main()
    