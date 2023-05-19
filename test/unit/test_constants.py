import common.constants as constants


def test_main():
    assert constants.AZURE_MGMT_URL != ""
    assert isinstance(constants.API_SUCCESS, int)
    assert isinstance(constants.API_RESOURCE_MOVE_OK, int)
    assert isinstance(constants.API_RESOURCE_MOVE_FAIL, int)
    assert isinstance(constants.API_TIMEOUT, int)
