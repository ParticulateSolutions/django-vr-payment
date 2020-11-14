# Create your views here.

from django.http import (
    HttpResponseBadRequest,
    Http404,
    HttpResponseRedirect,
    HttpResponse,
)
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from . import settings
from .models import VRPaymentBasicPayment
from .models.webhooks import VRPaymentWebhook
from .utils.webhooks import decrypt_webhook
from .wrapper import VRPaymentWrapper


class VRPaymentBasicCheckoutView(TemplateView):
    template_name = "vr_payment/checkout.html"

    def get(self, request, *args, **kwargs):
        basic_payment = VRPaymentBasicPayment.objects.get(
            merchant_transaction_id=kwargs.get("merchant_transaction_id")
        )
        if basic_payment.payment_responses.exists():
            return HttpResponseBadRequest(
                "This merchant_transaction_id has already been used."
            )
        kwargs.update({"basic_payment": basic_payment})
        return super(VRPaymentBasicCheckoutView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        basic_payment = kwargs.get("basic_payment")
        context.update(
            {
                "basic_payment": basic_payment,
                "vr_payment_src_url": settings.VR_PAYMENT_TEST_URL
                if basic_payment.sandbox
                else settings.VR_PAYMENT_LIVE_URL,
                "shopper_result_url": self.request.build_absolute_uri(
                    reverse(settings.VR_PAYMENT_SHOPPER_RESULT_URL_NAME)
                ),
            }
        )
        return context


class VRPaymentReturnView(View):
    basic_payment = None

    def get_error_url(self):
        return reverse(settings.VR_PAYMENT_ERROR_URL_NAME)

    def get_rejected_url(self):
        return reverse(settings.VR_PAYMENT_ERROR_URL_NAME)

    def get_pending_url(self):
        return reverse(settings.VR_PAYMENT_PENDING_URL_NAME)

    def get_success_url(self):
        return reverse(settings.VR_PAYMENT_SUCCESS_URL_NAME)

    def get_redirect_url(
        self, entity_id: str = None, bearer_token: str = None, sandbox: bool = None
    ):
        redirect_url = None
        # check if already successful
        latest_payment_response = self.basic_payment.payment_responses.last()
        if latest_payment_response:
            redirect_url = (
                self.get_success_url()
                if latest_payment_response
                == self.basic_payment.payment_responses.filter_successfully_processed().last()
                else None
            )

        if not redirect_url:
            # check status from VR Pay
            vr_payment_wrapper = VRPaymentWrapper(
                entity_id=entity_id, bearer_token=bearer_token, sandbox=sandbox
            )
            vr_payment_status = vr_payment_wrapper.get_checkout_status(
                basic_payment=self.basic_payment
            )
            if vr_payment_status.is_successful:
                self.basic_payment.payment_id = vr_payment_status.vr_pay_id
                redirect_url = self.get_success_url()
            elif vr_payment_status.is_rejected:
                redirect_url = self.get_rejected_url()
            elif vr_payment_status.is_pending:
                redirect_url = self.get_pending_url()
            else:
                redirect_url = self.get_error_url()
        return redirect_url

    def get(self, *args, **kwargs):
        update_fields = []
        try:
            self.basic_payment = VRPaymentBasicPayment.objects.get(
                checkout_response__vr_pay_id=self.request.GET["id"]
            )
            if self.basic_payment.resource_path:
                if self.basic_payment.resource_path != self.request.GET["resourcePath"]:
                    raise AssertionError(
                        f"resource_path for checkout_id: {self.request.GET['id']} changed to '{self.request.GET['resourcePath']}'"
                    )
            else:
                self.basic_payment.resource_path = self.request.GET["resourcePath"]
                update_fields.append("resource_path")
        except VRPaymentBasicPayment.DoesNotExist as e:
            raise Http404(e)
        except MultiValueDictKeyError as e:
            return HttpResponseBadRequest(f"expected keyword {e} not found")

        update_fields.append("payment_id")
        self.basic_payment.save(update_fields=update_fields)
        return HttpResponseRedirect(self.get_redirect_url())


@method_decorator(csrf_exempt, name="dispatch")
class VRPaymentWebhookView(View):
    config_key = settings.VR_PAYMENT_CONFIG_KEY

    def post(self, request, *args, **kwargs):
        VRPaymentWebhook.objects.create_from_request(self.config_key, self.request)
        return HttpResponse(status=202)  # Accepted
