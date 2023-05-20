from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient

import azure_helper.subscription_helper as sub_helper


def get_resource_client(source_subscription_id: str) -> ResourceManagementClient:
    '''
    Gets the resource client for the current AZ context
    '''
    # Acquire a credential object using CLI-based authentication.
    credential = AzureCliCredential()    

    #check for valid subscription ID
    if sub_helper.check_valid_subscription_id(source_subscription_id):
        # Obtain the management object for resources.
        return ResourceManagementClient(credential, source_subscription_id)    


def get_resource_ids(resource_client: str,
                     source_resource_group: str) -> list[str]:
    '''
    Gets the given resource IDs for a given resource group - returns a JSON str
    '''
    resources =  resource_client.resources.list_by_resource_group(
        source_resource_group, expand = "createdTime,changedTime")

    # get the resource ids as a list
    resource_ids = [resource.id for resource in resources]
    return resource_ids