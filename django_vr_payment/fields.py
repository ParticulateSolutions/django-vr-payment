from django.core import validators
from django.db import models

from django.utils.functional import cached_property


class VRPaymentDecimalField(models.DecimalField):
    """
    Decimalfield declared as described in https://vr-pay-ecommerce.docs.oppwa.com/reference/parameters#basic
    """

    def __init__(
        self, verbose_name=None, name=None, max_digits=12, decimal_places=2, **kwargs
    ):
        super().__init__(verbose_name, name, max_digits, decimal_places, **kwargs)

    @cached_property
    def validators(self):
        return super().validators + [
            validators.RegexValidator(regex="[0-9]{1,10}(\.[0-9]{2})?")
        ]
