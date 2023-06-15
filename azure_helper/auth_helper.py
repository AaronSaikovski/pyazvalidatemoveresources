"""
Azure Auth Helper
"""
from azure.core.credentials import AccessToken as AccessToken
from azure.identity import AzureCliCredential

import common.constants as constants

# ******************************************************************************** #


def get_az_cached_access_token() -> AccessToken:
    """
    Gets the cached access token from the AZ CLI session token
    """

    """Gets the cached access token from the AZ CLI session token

    Returns:
        AccessToken: Access token from scope
    """
    credential = AzureCliCredential()
    access_token = credential.get_token(constants.AZURE_MGMT_URL)
    return access_token.token


# ******************************************************************************** #
