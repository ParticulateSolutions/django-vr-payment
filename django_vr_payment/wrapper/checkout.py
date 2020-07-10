import json
from decimal import Decimal

import requests
from django.utils import timezone
from requests import Response

from ..models import (
    VRPaymentBasicPaymentStatusResponse,
    VRPaymentBasicPayment,
    VRPaymentCheckoutResponse,
)


class CheckOutWrapper(object):
    def create_checkout(
        self,
        amount: Decimal,
        payment_type: str,
        merchant_transaction_id: str,
        currency: str = "EUR",
        tax_amount: Decimal = Decimal(0.00),
        payment_brand: str = None,
        descriptor: str = None,
        merchant_invoice_id: str = None,
        merchant_memo: str = None,
        transaction_category: str = None,
        **kwargs,
    ) -> Response:
        """
        create a checkout. see VR Payment documentation for all available fields
        :param amount: complete payable amount as Decimal
        :param payment_type: one of VRPaymentBasicPayment.PAYMENT_TYPE
        :param merchant_transaction_id: Merchant-provided reference number, must be unique for your transactions
        :param currency: The currency code of the payment request's amount
        :param tax_amount: Tax amount as Decimal
        :param payment_brand: (optional) The brand specifies the method of payment for the request
        :param descriptor: (optional) Can be used to populate all or part of the Merchant Name descriptor, which often appears on the first line of the shopper's statement.
        :param merchant_invoice_id: (optional) Merchant-provided invoice number, should be unique for your transactions.
        :param merchant_memo: (optional) Merchant-provided additional information
        :param transaction_category: (optional) The category of the transaction. See VR Payment docs for possible values
        :param kwargs: (optional) any additional information you want to provide. See VR Payment docs for possible kwargs. NOTE: these values will not be saved in the VRPaymentBasicPayment object
        """
        data = {
            "entityId": self.entity_id,
            "amount": amount,
            "currency": currency,
            "paymentType": payment_type,
            "taxAmount": tax_amount,
            "paymentBrand": payment_brand,
            "descriptor": descriptor,
            "merchantTransactionId": merchant_transaction_id,
            "merchantInvoiceId": merchant_invoice_id,
            "merchantMemo": merchant_memo,
            "transactionCategory": transaction_category,
            **kwargs,  # additional information. You need to keep track of these yourself
        }
        response = self._call_api("/v1/checkouts", "POST", data=data)
        basic_payment = VRPaymentBasicPayment.objects.create(
            entity_id=self.entity_id,
            amount=amount,
            currency=currency,
            payment_type=payment_type,
            tax_amount=tax_amount,
            payment_brand=payment_brand,
            descriptor=descriptor,
            merchant_transaction_id=merchant_transaction_id,
            merchant_invoice_id=merchant_invoice_id,
            merchant_memo=merchant_memo,
            transaction_category=transaction_category,
            sandbox=self.sandbox,
        )
        VRPaymentCheckoutResponse.objects.create_from_response(
            response, basic_payment=basic_payment
        )
        return basic_payment

    def get_checkout_status(
        self, basic_payment: VRPaymentBasicPayment
    ) -> VRPaymentBasicPaymentStatusResponse:
        url = f"{basic_payment.resource_path}?entityId={self.entity_id}"
        try:
            assert basic_payment.created_at > (
                timezone.now() - timezone.timedelta(minutes=30)
            )
            response = self._call_api(url, "GET")
            response.raise_for_status()
        except (AssertionError, requests.HTTPError):
            # checkout status can only be retrieved once for 30 min
            # or initial checkout status might already be handled but missing;
            # -> try with merchant_transaction_id
            if basic_payment.merchant_transaction_id:
                return self.get_transaction_by_merchant_transaction_id(basic_payment)
        return VRPaymentBasicPaymentStatusResponse.objects.create_from_response(
            response, basic_payment=basic_payment
        )
