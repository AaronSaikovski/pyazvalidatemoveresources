"""
Validates a source Azure resource group and all child resources to check 
for moveability support into a target resource group within a target subscription.

This script takes a Source SubscriptionID and Source ResourceGroup as 
parameters, analyzes the subscription/resource group.
and gathers a list of resource Ids and excludes those 
resources that cannot be moved based on the resource ID list.
"""
import os
#import pprint
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
            logger.exception(f"Exception raised in {func.__name__}. exception: {str(ex)}")
            raise ex
    return wrapper

@log
def get_resource_client(source_subscription_id: str) -> object:
    '''
    Gets the resource client for the current AZ context
    '''
    # Acquire a credential object using CLI-based authentication.
    credential = AzureCliCredential()

    # Obtain the management object for resources.
    resource_client = ResourceManagementClient(credential, source_subscription_id)
    return resource_client

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
    Gets the given resource IDs for a given resource group - returns a list[]
    '''
    resource_list = resource_client.resources.list_by_resource_group(
        source_resource_group, expand = "createdTime,changedTime")

    # get the resource ids as a list
    resource_ids = []
    for resource in enumerate(list(resource_list)):
        resource_ids.append(resource.id)
    return resource_ids


def create_request_header(cached_access_token: str) -> str:
    '''
    Creates a request header to pass to the API call
    '''
     #get the bearer token
    bearer_token = f"Bearer {cached_access_token}"

    #build the request header and convert ' to ".
    request_header = str({'Content-Type':'application/json',
                          'Authorization':bearer_token}).replace("'", '"')
    return request_header

@log
def create_request_body(target_subscription_id:str,
                        target_resource_group: str,
                        resource_ids: str) -> str:
    '''
    Creates a request body to pass to the API
    '''
    target_resource_group = str(f"/subscriptions/{target_subscription_id}"
                                "/resourceGroups/{target_resource_group}")
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
    #Build the API and call it and get the response code
    # pylint: disable=line-too-long
    validate_move_api = f"https://management.azure.com/subscriptions/{source_subscription_id}/resourceGroups/{source_resource_group}validateMoveResources?api-version=2021-04-01"
    api_response = requests.post(url=validate_move_api,
                                 headers=request_header,
                                 data=request_body,
                                 timeout=20)
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

    #build the request header - passing in the access token
    request_header = create_request_header(get_az_cached_access_token())

    #build the body of the request to be passed to the API
    request_body = create_request_body(target_subscription_id, target_resource_group, resource_ids)
    #print(f"Req body = {request_body}")

    #Call the API and get a response code back
    # api_response = call_validate_api(source_subscription_id,
    #                                  source_resource_group,
    #                                  request_header, request_body)
    # pprint.pprint(api_response)

# call main
if __name__ == '__main__':
    main()
    