from rongcloud_server_mcp.sdk.exceptions import (
    APIErrorDetail,
    RongCloudAPIError,
    RongCloudError,
    RongCloudRequestError,
    RongCloudValidationError,
)


def test_api_error_detail_fields():
    """Test that APIErrorDetail correctly stores code, message, and http_status.

    Verifies that the default value of http_status is 200 when not provided.
    """
    # Without specifying http_status (should default to 200)
    detail1 = APIErrorDetail(code=400, message='Bad Request')
    assert detail1.code == 400
    assert detail1.message == 'Bad Request'
    assert detail1.http_status == 200

    # Specifying all fields explicitly
    detail2 = APIErrorDetail(code=500, message='Server Error', http_status=500)
    assert detail2.code == 500
    assert detail2.message == 'Server Error'
    assert detail2.http_status == 500


def test_rongcloud_api_error_message_and_detail():
    """Test RongCloudAPIError initialization and string representation.

    Ensures that the error_detail is properly stored and __str__ returns
    the expected formatted error message.
    """
    detail = APIErrorDetail(code=404, message='Not Found', http_status=404)
    exc = RongCloudAPIError(detail)

    assert exc.error_detail is detail
    assert str(exc) == 'HTTP 404 - [404] Not Found'
    assert isinstance(exc, RongCloudError)


def test_rongcloud_request_error_default_and_custom_message():
    """Test RongCloudRequestError with and without a custom message.

    Verifies that the default message is "Request failed" and a custom
    message can be passed and returned properly.
    """
    exc_default = RongCloudRequestError()
    assert isinstance(exc_default, RongCloudError)
    assert str(exc_default) == 'Request failed'

    exc_custom = RongCloudRequestError('Network unreachable')
    assert str(exc_custom) == 'Network unreachable'


def test_rongcloud_validation_error_default_and_custom():
    """Test RongCloudValidationError with and without a custom message.

    Ensures the default message is "Validation failed" and that a custom
    message is accepted and displayed correctly.
    """
    exc_def = RongCloudValidationError()
    assert isinstance(exc_def, RongCloudError)
    assert str(exc_def) == 'Validation failed'

    exc_cust = RongCloudValidationError('Field X is missing')
    assert str(exc_cust) == 'Field X is missing'


def test_exception_inheritance():
    """Test that all specific exceptions inherit from RongCloudError.

    This includes RongCloudAPIError, RongCloudRequestError, and RongCloudValidationError.
    """
    detail = APIErrorDetail(code=1, message='msg')
    api_exc = RongCloudAPIError(detail)
    req_exc = RongCloudRequestError()
    val_exc = RongCloudValidationError()

    for e in (api_exc, req_exc, val_exc):
        assert isinstance(e, RongCloudError)
