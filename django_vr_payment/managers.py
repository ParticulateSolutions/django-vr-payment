import json

from django.db.models import Q, QuerySet
from django.db.models.manager import Manager

from .utils.transaction_status import (
    TRANSACTION_SUCCESSFULLY_PROCESSED_REGEX,
    TRANSACTION_SUCCESSFULLY_PROCESSED_NEEDS_REVIEW_REGEX,
    TRANSACTION_PENDING_REGEX,
    TRANSACTION_PENDING_MIGHT_CHANGE_EXTERNALLY_REGEX,
)


class VRPaymentBasicPaymentManager(Manager):
    def get(self, *args, **kwargs):
        return super().select_related("checkout_response").get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        return super().select_related("checkout_response").filter(*args, **kwargs)


class VRPaymentAPIResponseManger(Manager):
    def create_from_response(
        self, response, basic_payment=None,
    ):
        response_json = response.json()
        if "payments" in response_json:
            # querying the transaction status can return several payments, but we currently only support one
            assert len(response_json["payments"]) == 1, "too many payments in response"
            response_json.update(response_json["payments"].pop())
        vr_response = self.model(
            basic_payment=basic_payment,
            http_status_code=response.status_code,
            url=response.url,
            raw_headers=json.dumps(dict(response.headers)),
            raw_content=response.json(),  # response_json might have been altered already; save the raw json!
            build_number=response_json.get("buildNumber"),
            ndc=response_json.get("ndc"),
            vr_pay_id=response_json.get("id"),
            reference_id=response_json.get("referencedId"),
            payment_brand=response_json.get("paymentBrand"),
            amount=response_json.get("amount"),
            currency=response_json.get("currency"),
            descriptor=response_json.get("descriptor"),
            result_code=response_json["result"].get("code"),
            result_description=response_json["result"].get("description"),
            result_avs_response=response_json["result"].get("avsResponse"),
            result_cvv_response=response_json["result"].get("cvvResponse"),
            result_details=response_json.get("resultDetails"),
            result_details_acquirer_response=response_json["resultDetails"].get(
                "AcquirerResponse"
            )
            if "resultDetails" in response_json
            else None,
            card_bin=response_json["card"].get("bin")
            if "card " in response_json
            else None,
            card_holder=response_json["card"].get("holder")
            if "card " in response_json
            else None,
            card_expiry_month=response_json["card"].get("expiryMonth")
            if "card " in response_json
            else None,
            card_expiry_year=response_json["card"].get("expiryYear")
            if "card " in response_json
            else None,
            merchant_bank_account_holder=response_json["merchant"]["bankAccount"].get(
                "holder"
            )
            if "merchant" in response_json
            and "bankAccount" in response_json["merchant"]
            else None,
            merchant_bank_account_nummber=response_json["merchant"]["bankAccount"].get(
                "nummber"
            )
            if "merchant" in response_json
            and "bankAccount" in response_json["merchant"]
            else None,
            merchant_bank_account_bic=response_json["merchant"]["bankAccount"].get(
                "bic"
            )
            if "merchant" in response_json
            and "bankAccount" in response_json["merchant"]
            else None,
            merchant_bank_account_country=response_json["merchant"]["bankAccount"].get(
                "country"
            )
            if "merchant" in response_json
            and "bankAccount" in response_json["merchant"]
            else None,
            risk_score=response_json["risk"].get("score")
            if "risk" in response_json
            else None,
            other=response_json.get("Other"),
        )
        vr_response.save()
        return vr_response

    def filter_successfully_processed_all(self) -> QuerySet:
        return self.filter(
            Q(result_code__regex=TRANSACTION_SUCCESSFULLY_PROCESSED_REGEX)
            | Q(
                result_code__regex=TRANSACTION_SUCCESSFULLY_PROCESSED_NEEDS_REVIEW_REGEX
            )
        )

    def filter_successfully_processed(self) -> QuerySet:
        return self.filter(result_code__regex=TRANSACTION_SUCCESSFULLY_PROCESSED_REGEX)

    def filter_successfully_processed_needs_review(self) -> QuerySet:
        return self.filter(
            result_code__regex=TRANSACTION_SUCCESSFULLY_PROCESSED_NEEDS_REVIEW_REGEX
        )

    def filter_pending_all(self) -> QuerySet:
        return self.filter(
            Q(result_code__regex=TRANSACTION_PENDING_REGEX)
            | Q(result_code__regex=TRANSACTION_PENDING_MIGHT_CHANGE_EXTERNALLY_REGEX)
        )

    def filter_pending(self) -> QuerySet:
        return self.filter(result_code__regex=TRANSACTION_PENDING_REGEX)

    def filter_pending_might_change(self) -> QuerySet:
        return self.filter(
            result_code__regex=TRANSACTION_PENDING_MIGHT_CHANGE_EXTERNALLY_REGEX
        )
