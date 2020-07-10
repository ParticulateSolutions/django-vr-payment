from django.conf import settings

DJANGO_VR_PAYMENT_VERSION = "0.0.1"

# VR Payment Settings
VR_PAYMENT_BEARER_TOKEN = getattr(
    settings,
    "VR_PAYMENT_BEARER_TOKEN",
    "OGE4Mjk0MTc0ZTczNWQwYzAxNGU3OGJlYjZjNTE1NGZ8Y1RaakFtOWM4Nw==",
)
VR_PAYMENT_ENTITY_ID = getattr(
    settings, "VR_PAYMENT_ENTITY_ID", "8a8294174e735d0c014e78beb6b9154b"
)

VR_PAYMENT_SANDBOX = getattr(settings, "VR_PAYMENT_SANDBOX", True)
VR_PAYMENT_TEST_URL = getattr(
    settings, "VR_PAYMENT_TEST_URL", "https://test.vr-pay-ecommerce.de/"
)
VR_PAYMENT_LIVE_URL = getattr(
    settings, "VR_PAYMENT_LIVE_URL", "https://vr-pay-ecommerce.de/"
)


# Internal Settings
VR_PAYMENT_SHOPPER_RESULT_URL_NAME = getattr(
    settings, "VR_PAYMENT_SHOPPER_RESULT_URL_NAME", "vr-payment:return"
)
VR_PAYMENT_ERROR_URL_NAME = getattr(
    settings, "VR_PAYMENT_ERROR_URL_NAME", "vr-payment:status-error"
)
VR_PAYMENT_REJECTED_URL_NAME = getattr(
    settings, "VR_PAYMENT_REJECTED_URL_NAME", "vr-payment:status-rejected"
)
VR_PAYMENT_PENDING_URL_NAME = getattr(
    settings, "VR_PAYMENT_PENDING_URL_NAME", "vr-payment:status-pending"
)
VR_PAYMENT_SUCCESS_URL_NAME = getattr(
    settings, "VR_PAYMENT_SUCCESS_URL_NAME", "vr-payment:status-success"
)
