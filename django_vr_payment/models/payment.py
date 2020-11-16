from django.core.exceptions import MultipleObjectsReturned
from django.core.validators import (
    MinLengthValidator,
    RegexValidator,
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

from .core import BaseModel
from .mixins import (
    VRPaymentResultMixin,
    VRPaymentResultDetails,
    VRPayApiResponseMixin,
    VRPaymentCardMixin,
    VRPaymentMerchantMixin,
)
from .webhooks import VRPaymentWebhook


from ..fields import VRPaymentDecimalField, JSONField
from ..managers import VRPaymentAPIResponseManger, VRPaymentBasicPaymentManager
from ..utils.transaction_status import (
    check_transaction_successful,
    check_transaction_pending,
    check_transaction_rejected,
)


class AbstractVRPaymentResponse(
    VRPayApiResponseMixin,
    VRPaymentResultMixin,
    VRPaymentResultDetails,
    VRPaymentCardMixin,
    VRPaymentMerchantMixin,
    BaseModel,
):
    """
    all Payment Response Parameters
    from https://vr-pay-ecommerce.docs.oppwa.com/reference/parameters#response-params

    """

    vr_pay_id = models.CharField(
        "ID",
        blank=True,
        help_text="The VR Pay identifier of this object",
        max_length=48,
        null=True,  # blank/null True b/c the request could have been invalid
    )
    reference_id = models.CharField(
        "ReferenceID",
        blank=True,
        help_text="In case of referenced payment (e.g., Capture or Refund), this fields included to see which payment was referenced.",
        max_length=32,
        null=True,
        validators=[RegexValidator(regex=r"[a-zA-Z0-9]{32}")],
    )
    payment_brand = models.CharField(
        "Payment brand",
        blank=True,
        help_text="The payment brand of the request.",
        max_length=32,
        null=True,
        validators=[RegexValidator(regex=r"[a-zA-Z0-9_] {1,32}")],
    )
    amount = VRPaymentDecimalField(
        "Amount", blank=True, help_text="The amount of the request", null=True,
    )
    currency = models.CharField(
        "Currency",
        blank=False,
        default="EUR",
        help_text="The ISO 4217 currency code of the payment request's amount",
        max_length=3,
        null=True,
    )
    descriptor = models.CharField(
        "Descriptor",
        blank=True,
        help_text="The descriptor of the request.",
        max_length=127,
        null=True,
    )
    risk_score = models.IntegerField(
        "Risk score",
        blank=True,
        help_text="Returns the score of the executed transaction risk checks. The value is a number from -99999 to +99999. Can be returned both for standalone risk requests and payment requests that include risk checks.",
        validators=[MinValueValidator(-99999), MaxValueValidator(99999)],
        null=True,
    )
    merchant_transaction_id = models.CharField(
        "Merchant transaction ID",
        blank=False,
        help_text="Merchant-provided reference number, should be unique for your transactions. "
        "Some receivers require this ID. This identifier is often used for reconciliation.",
        max_length=255,
        validators=[MinLengthValidator(8)],
    )
    other = JSONField(
        "Other",
        blank=True,
        help_text="The response can also contain each of the data structures listed above, such as 'customer' and 'billingAddress'.",
        null=True,
    )

    objects = VRPaymentAPIResponseManger()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["vr_pay_id"]),
            models.Index(fields=["reference_id"]),
        ]

    def __str__(self):
        return f"{self._meta.model_name}[{self.id}] - {self.http_status_code}"

    @property
    def is_successful(self) -> bool:
        return check_transaction_successful(self.result_code)

    @property
    def is_pending(self) -> bool:
        return check_transaction_pending(self.result_code)

    @property
    def is_rejected(self) -> bool:
        return check_transaction_rejected(self.result_code)


class VRPaymentBasicPayment(BaseModel):
    """
    implementation of Basic Payment
    https://vr-pay-ecommerce.docs.oppwa.com/reference/parameters#basic
    """

    PREAUTHORIZATION = "PA"
    DEBIT = "DB"
    CREDIT = "CD"
    CAPTURE = "CP"
    REVERSAL = "RV"
    REFUND = "RF"
    PAYMENT_TYPE = [
        (PREAUTHORIZATION, _("Preauthorization")),
        (DEBIT, _("Debit")),
        (CREDIT, _("Credit")),
        (CAPTURE, _("Capture")),
        (REVERSAL, _("Reversal")),
        (REFUND, _("Refund")),
    ]
    entity_id = models.CharField(
        "Entity ID",
        blank=False,
        null=False,
        help_text="The entity required to authorize the request. "
        "This should be the channel entity identifier. "
        "In case channel dispatching is activated then it should be the merchant entity identifier.",
        max_length=32,
    )
    amount = VRPaymentDecimalField(
        "Amount",
        help_text="Indicates the amount of the payment request. "
        "The dot is used as decimal separator. "
        "The amount is the only amount value which is processing relevant. "
        "All other amount declarations like taxAmount or shipping.cost are already included.",
    )
    tax_amount = VRPaymentDecimalField(
        "Tax amount", help_text="Indicates the tax amount of the payment request."
    )
    currency = models.CharField(
        "Currency",
        blank=False,
        default="EUR",
        help_text="The ISO 4217 currency code of the payment request's amount",
        max_length=3,
    )
    payment_brand = models.CharField(
        "Payment brand",
        blank=True,
        help_text="The brand specifies the method of payment for the request. "
        "This is optional if you want to use brand detection for credit cards, if not then it is mandatory.",
        max_length=32,
        null=True,
        validators=[RegexValidator(regex=r"[a-zA-Z0-9_]{1,32}")],
    )
    payment_type = models.CharField(
        "Payment type",
        blank=False,
        choices=PAYMENT_TYPE,
        help_text="The payment type for the request. See docs for supported types",
        max_length=2,
    )
    descriptor = models.CharField(
        "Descriptor",
        blank=True,
        help_text="Can be used to populate all or part of the Merchant Name descriptor, "
        "which often appears on the first line of the shopper's statement. "
        "The full use of this field depends on the Merchant Account configuration. "
        "NOTE: merchant.name can override any data sent in this field.",
        max_length=127,
        null=True,
    )
    merchant_transaction_id = models.CharField(
        "Merchant transaction ID",
        blank=False,
        help_text="Merchant-provided reference number, should be unique for your transactions. "
        "Some receivers require this ID. This identifier is often used for reconciliation.",
        max_length=255,
        unique=True,
        validators=[MinLengthValidator(8)],
    )
    merchant_invoice_id = models.CharField(
        "Merchant invoice ID",
        blank=True,
        help_text="Merchant-provided invoice number, should be unique for your transactions. "
        "This identifier is not sent onwards.",
        max_length=255,
        null=True,
        unique=True,
        validators=[MinLengthValidator(8)],
    )
    merchant_memo = models.CharField(
        "Merchant memo",
        blank=True,
        help_text="Merchant-provided additional information. The information provided is not transaction processing relevant. "
        "It will appear in reporting only.",
        max_length=255,
        null=True,
        validators=[MinLengthValidator(8)],
    )
    transaction_category = models.CharField(
        "Transaction category",
        blank=True,
        help_text="The category of the transaction. See docs for possible values:",
        max_length=32,
        null=True,
    )
    sandbox = models.BooleanField(
        "Sandbox", help_text="Determine if this transaction uses the Test or Live host"
    )
    resource_path = models.CharField(
        "VR Payment Resource Path",
        blank=True,
        default="",
        help_text="VR Payment resource path can. Can be used to get the status",
        max_length=512,
        null=True,
    )
    payment_id = models.CharField(
        "VR Payment ID",
        blank=True,
        default="",
        help_text="The identifier of the payment request that can be used to reference the payment later",
        max_length=32,
        null=True,
        validators=[RegexValidator(r"[a-zA-Z0-9]{32}")],
    )
    objects = VRPaymentBasicPaymentManager()

    class Meta:
        verbose_name = "VR Payment Basic Payment Checkout"
        verbose_name_plural = "VR Payment Basic Checkouts"
        indexes = [
            models.Index(fields=["merchant_transaction_id"]),
            models.Index(fields=["merchant_invoice_id"]),
        ]

    def __str__(self):
        return f"id: {self.id}, transaction_id: {self.merchant_transaction_id} ({self.amount} {self.currency})"

    @property
    def checkout_id(self):
        return self.checkout_response.vr_pay_id


class VRPaymentBasicPaymentStatusResponse(AbstractVRPaymentResponse):
    basic_payment = models.ForeignKey(
        VRPaymentBasicPayment,
        on_delete=models.CASCADE,
        related_name="payment_responses",
        verbose_name=VRPaymentBasicPayment._meta.verbose_name_plural,
    )

    class Meta:
        verbose_name = "VR Payment Payment Response"
        verbose_name_plural = "VR Payment Payment Responses"


class VRPaymentCheckoutResponse(AbstractVRPaymentResponse):
    basic_payment = models.OneToOneField(
        VRPaymentBasicPayment,
        on_delete=models.CASCADE,
        related_name="checkout_response",
        verbose_name=VRPaymentBasicPayment._meta.verbose_name,
    )

    class Meta:
        verbose_name = "VR Payment Checkout Reponse"
        verbose_name_plural = "VR Payment Checkout Reponses"


class VRPaymentWebhookPaymentPayload(AbstractVRPaymentResponse):
    basic_payment = models.ForeignKey(
        VRPaymentBasicPayment,
        on_delete=models.CASCADE,
        related_name="webhook_responses",
        verbose_name=VRPaymentBasicPayment._meta.verbose_name_plural,
    )
    webhook = models.OneToOneField(
        VRPaymentWebhook,
        on_delete=models.CASCADE,
        related_name="payment_payload",
        verbose_name="VR Payment Webhook Payload",
    )

    class Meta:
        verbose_name = "VR Payment Webhook Payload"
        verbose_name_plural = "VR Payment Webhook Payloads"
