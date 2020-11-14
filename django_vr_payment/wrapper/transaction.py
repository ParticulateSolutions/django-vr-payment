import logging

import requests

from ..models import VRPaymentBasicPayment, VRPaymentBasicPaymentStatusResponse

logger = logging.getLogger(__name__)


class TransactionWrapper(object):
    """
    https://vr-pay-ecommerce.docs.oppwa.com/tutorials/reporting/transaction
    """

    def _get_transaction_status(
        self, url: str, basic_payment: VRPaymentBasicPayment
    ) -> VRPaymentBasicPaymentStatusResponse:
        try:
            response = self._call_api(url, "GET")
            response.raise_for_status()
        except requests.HTTPError as e:
            # log error, save error
            logger.error(e)
        return VRPaymentBasicPaymentStatusResponse.objects.create_from_response(
            response, basic_payment=basic_payment
        )

    def get_transaction_by_payment_id(
        self, basic_payment: VRPaymentBasicPayment
    ) -> VRPaymentBasicPaymentStatusResponse:
        url = (
            f"v1/query/{getattr(basic_payment, 'payment_id')}?entityId={self.entity_id}"
        )
        return self._get_transaction_status(url, basic_payment)

    def get_transaction_by_merchant_transaction_id(
        self, basic_payment: VRPaymentBasicPayment
    ) -> VRPaymentBasicPaymentStatusResponse:
        url = f"v1/query?entityId={self.entity_id}&merchantTransactionId={getattr(basic_payment, 'merchant_transaction_id')}"
        return self._get_transaction_status(url, basic_payment)
