from django.db import models
from django.utils.translation import gettext_lazy as _

from django_vr_payment.managers import VRPaymentWebhookManager

try:
    # Django 3.1
    from django.db.models import JSONField as BaseJSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField as BaseJSONField

from django_vr_payment.models.core import BaseModel


class VRPaymentWebhook(BaseModel):
    raw_headers = BaseJSONField("Headers", help_text="response header as json")
    webhook_type = models.CharField(
        "Webhook type",
        blank=False,
        help_text="The webhook type. Can be PAYMENT, REGISTRATION, RISK (and others in test…)",
        max_length=64,  # don't actually know; test environment != docs…
        null=False,
    )
    webhook_action = models.CharField(
        "Webhook action",
        blank=True,
        help_text="The webhook action. Only applies to REGISTRATION type (and others in test…)",
        max_length=64,  # don't actually know; test environment != docs…
        null=True,
    )
    decrypted_body = BaseJSONField(
        "Decrypted body",
        blank=False,
        help_text="The decrypted request.body in JSON",
        null=False,
    )

    objects = VRPaymentWebhookManager()

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert, force_update, using, update_fields)
        if self.webhook_type is "payment":
            if not self.payment_payload:
                from django_vr_payment.models.payment import (
                    VRPaymentWebhookPaymentPayload,
                )

                VRPaymentWebhookPaymentPayload.objects.create_from_response(
                    self.decrypted_payload
                )
