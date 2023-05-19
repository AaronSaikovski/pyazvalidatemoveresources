
import re

def check_valid_subscription_id(subscription_id: str) -> bool:
    '''
    checks for a valid Azure Subscription ID - Format 00000000-0000-0000-0000-000000000000
    '''
    # check if a string
    if isinstance(subscription_id, str):
        # pylint: disable=line-too-long
        # pylint: disable=anomalous-backslash-in-string
        re_result = re.search("^(\{{0,1}([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}\}{0,1})$", subscription_id)
        return bool(re_result)
    return False