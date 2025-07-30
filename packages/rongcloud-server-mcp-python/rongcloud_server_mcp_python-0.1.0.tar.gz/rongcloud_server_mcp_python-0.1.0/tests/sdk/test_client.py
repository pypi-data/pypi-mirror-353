from rongcloud_server_mcp.sdk.client import RongCloudClient


def test_rongcloud_client_properties_not_none():
    """Test that RongCloudClient initializes with all expected attributes.

    Verifies that the `users`, `messages`, and `groups` properties are not None,
    and that base attributes like `app_key`, `app_secret`, and `api_base` are
    correctly assigned during initialization.
    """
    client = RongCloudClient(
        app_key='dummy_key',
        app_secret='dummy_secret',
        api_base='https://api-cn.ronghub.com',
        api_timeout=10,
    )

    assert client.users is not None
    assert client.messages is not None
    assert client.groups is not None

    assert client.app_key == 'dummy_key'
    assert client.app_secret == 'dummy_secret'
    assert client.api_base == 'https://api-cn.ronghub.com'
