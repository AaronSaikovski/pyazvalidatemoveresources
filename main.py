#!/usr/bin/env python
"""
Validates a source Azure resource group and all child resources to check 
for moveability support into a target resource group within a target subscription.

This script takes a Source SubscriptionID and Source ResourceGroup as 
parameters, analyzes the subscription/resource group.
and gathers a list of resource Ids and excludes those 
resources that cannot be moved based on the resource ID list.

Usage:
      python3 main.py --SourceSubscriptionId "XXXX-XXXX-XXXX-XXXX" 
                      --SourceResourceGroup "SourceRSG" 
                      --TargetSubscriptionId "XXXX-XXXX-XXXX-XXXX" 
                      --TargetResourceGroup "TargetRSG"
"""
__author__ = "Aaron Saikovski"
__contact__ = "asaikovski@outlook.com"
__license__ = "MIT"
__maintainer__ = "developer"
__status__ = "Production"
__version__ = "3.0.0"


import argparse

import azure_helper.api_helper as api_helper
import azure_helper.auth_helper as auth_helper
import azure_helper.request_helper as req_helper
import azure_helper.resource_client_helper as res_client_helper
import utils.console_helper as console_helper

# Custom modules
import utils.logging_helper as logging_helper


@logging_helper.log
def main() -> None:
    '''
    Main method
    '''

    # help message string
    # pylint: disable=line-too-long
    help_msg: str = (
        "Validates a source Azure resource group" 
        "and all child resources to check for moveability support into a target"
        " resource group within a target subscription."
    )

    # add Args
    parser = argparse.ArgumentParser(description=help_msg)
    parser.add_argument('--SourceSubscriptionId', 
                        '-srcsubid', 
                        required=True, 
                        help='Source Subscription Id.')
    parser.add_argument('--SourceResourceGroup', 
                        '-srcrsg', 
                        required=True, 
                        help='Source Resource Group.')
    parser.add_argument('--TargetSubscriptionId', 
                        '-targsubid', 
                        required=True, 
                        help='Target Subscription Id.')
    parser.add_argument('--TargetResourceGroup', 
                        '-targrsg',
                          required=True,
                         help='Target Resource Group.')
    args = parser.parse_args()

    # set values from command line
    source_subscription_id = args.SourceSubscriptionId
    source_resource_group = args.SourceResourceGroup
    target_subscription_id = args.TargetSubscriptionId
    target_resource_group = args.TargetResourceGroup

    console_helper.print_ok_message("***STARTED PROCESSING***")

    # Obtain the management object for resources.
    resource_client = res_client_helper.get_resource_client(source_subscription_id)

    # Get the resource IDs
    resource_ids = res_client_helper.get_resource_ids(resource_client, 
                                                      source_resource_group)

    # Build the request header - passing in the access token
    request_header = req_helper.create_request_header(auth_helper.get_az_cached_access_token())

    # Build the body of the request to be passed to the API
    request_body = req_helper.create_request_body(target_subscription_id, 
                                                  target_resource_group, 
                                                  resource_ids)

    # Call the API and get a response code back
    api_response = api_helper.call_validate_api(
        source_subscription_id, source_resource_group, request_header, request_body
    )

    # Call the management API
    api_helper.call_management_api(api_response, request_header)

    console_helper.print_ok_message("***COMPLETED PROCESSING***")


# call main
if __name__ == '__main__':
    main()
