from django.db import models

try:
    # Django 3.1
    from django.db.models import JSONField as BaseJSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField as BaseJSONField


class APIResponseMixin(models.Model):
    http_status_code = models.IntegerField(
        "HTTP status code",
        help_text="response status code"
    )
    url = models.URLField(
        "URL",
        help_text="request url")
    raw_headers = BaseJSONField(
        "Headers",
        help_text="response header as json")
    raw_content = BaseJSONField(
        "Content",
        help_text="response content as json")

    class Meta:
        abstract = True


class VRPayApiResponseMixin(APIResponseMixin):
    build_number = models.CharField(
        "API response build number",
        blank=True,
        help_text="Useful for support purposes.",
        max_length=255,
        null=True,
    )
    ndc = models.CharField(
        "ndc",
        blank=True,
        help_text="An internal unique identifier for the request.",
        max_length=65,
        null=True,
    )

    class Meta:
        abstract = True


class VRPaymentResultMixin(models.Model):
    result_code = models.CharField(
        "VR Payment status code",
        blank=True,
        help_text="Status Code from VR Payment. see content for description",
        max_length=11,  # xxx.yyy.zzz
        null=True,
    )  # https://vr-pay-ecommerce.docs.oppwa.com/reference/resultCodes
    result_description = models.CharField(
        "Result Description",
        blank=True,
        help_text="A textual description explaining the result.code's meaning.",
        max_length=255,
        null=True,
    )
    result_avs_response = models.CharField(
        "Result avs response",
        blank=True,
        help_text="Contains the AVS response returned by the acquirer. It may include one the following result:"
                  "A = Address does match, zip code does not match"
                  "Z = Address does not match, zip code does match"
                  "N = Address and zip code do not match"
                  "U = Technical or logical error. AVS cannot be applied on card or address (not UK or US issuer), issuer is not available, etc."
                  "F = Address and Postal Code Matches",
        max_length=1,
        null=True,
    )
    result_cvv_response = models.CharField(
        "Result cvv response",
        blank=True,
        help_text="Contains the CVV response returned by the acquirer.",
        max_length=1,
        null=True,
    )

    class Meta:
        abstract = True


class VRPaymentResultDetails(models.Model):
    result_details = BaseJSONField(
        "Result details",
        blank=True,
        help_text="A container for name value pair used for enriching the response with bank-specific response details. I.e. the actual parameters used within resultDetails are bank-specific.",
        null=True,
    )
    result_details_acquirer_response = BaseJSONField(
        "Result details - Acquirer response",
        blank=True,
        help_text="Represents the acquirer original response code retrieved from the acquirer directly.",
        null=True,
    )

    class Meta:
        abstract = True


class VRPaymentCardMixin(models.Model):
    card_bin = models.CharField(
        "Card bin",
        blank=True,
        help_text="The first six digits of the card.number",
        max_length=6,
        null=True,
    )
    card_holder = models.CharField(
        "Card holder",
        blank=True,
        help_text="Holder of the credit card account",
        max_length=6,
        null=True,
    )
    card_expiry_month = models.CharField(
        "Card expiry month",
        blank=True,
        help_text="The expiry month of the card",
        max_length=2,
        null=True,
    )
    card_expiry_year = models.CharField(
        "Card expiry year",
        blank=True,
        help_text="The expiry year of the card",
        max_length=4,
        null=True,
    )

    class Meta:
        abstract = True


class VRPaymentMerchantMixin(models.Model):
    merchant_bank_account_holder = models.CharField(
        "Merchant bank account holder",
        blank=True,
        help_text="Holder of the merchant's bank account",
        max_length=128,
        null=True,
    )
    merchant_bank_account_nummber = models.CharField(
        "Merchant bank account nummber",
        blank=True,
        help_text="The account number of the merchant's bank account. (IBAN for SEPA accounts)",
        max_length=64,
        null=True,
    )
    merchant_bank_account_bic = models.CharField(
        "Merchant bank account bic",
        blank=True,
        help_text="The BIC (Bank Identifier Code (SWIFT)) number of the merchant's bank account.",
        max_length=11,
        null=True,
    )
    merchant_bank_account_country = models.CharField(
        "Merchant bank account country",
        blank=True,
        help_text="The country code of the merchant's bank account (ISO 3166-1).",
        max_length=2,
        null=True,
    )

    class Meta:
        abstract = True
