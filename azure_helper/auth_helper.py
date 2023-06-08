"""
Azure Auth Helper
"""
from azure.identity import AzureCliCredential

import common.constants as constants

# ******************************************************************************** #


def get_az_cached_access_token() -> object:
    """
    Gets the cached access token from the AZ CLI session token
    """
    credential = AzureCliCredential()
    access_token = credential.get_token(constants.AZURE_MGMT_URL)
    return access_token.token


# ******************************************************************************** #
