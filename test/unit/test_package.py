import azure_helper.subscription_helper as sub_helper


def test_main():
    assert sub_helper.check_valid_subscription_id("00000000-0000-0000-0000-000000000000") is not False
