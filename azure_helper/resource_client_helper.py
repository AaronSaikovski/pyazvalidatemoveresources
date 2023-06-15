"""
Azure ResourceClient Helper
"""

from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient

# ******************************************************************************** #

def get_resource_client(source_subscription_id: str) -> ResourceManagementClient:
    """
    Gets the resource client for the current AZ context
    """
    # Acquire a credential object using CLI-based authentication.
    credential = AzureCliCredential()
    return ResourceManagementClient(credential, source_subscription_id)

# ******************************************************************************** #

#     # get the resource ids as a list
def get_resource_ids(resource_client: str, source_resource_group: str) -> list[str]:
    """
    Gets the given resource IDs for a given resource group - returns a JSON str
    """
    resources = resource_client.resources.list_by_resource_group(
        source_resource_group, expand="createdTime,changedTime"
    )

    # get the resource ids as a list
    return [resource.id for resource in resources]
    

# ******************************************************************************** #
