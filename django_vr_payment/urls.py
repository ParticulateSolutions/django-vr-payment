# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "vr_payment"


urlpatterns = [
    path(
        "checkout/<str:merchant_transaction_id>/",
        views.VRPaymentBasicCheckoutView.as_view(),
        name="checkout",
    ),
    path("return/", views.VRPaymentReturnView.as_view(), name="return"),
    path(
        "status/pending/",
        TemplateView.as_view(
            template_name="vr_payment/status.html", extra_context={"status": "pending"}
        ),
        name="status-pending",
    ),
    path(
        "status/rejected/",
        TemplateView.as_view(
            template_name="vr_payment/status.html", extra_context={"status": "rejected"}
        ),
        name="status-rejected",
    ),
    path(
        "status/success/",
        TemplateView.as_view(
            template_name="vr_payment/status.html", extra_context={"status": "success"}
        ),
        name="status-success",
    ),
    path(
        "status/error/",
        TemplateView.as_view(
            template_name="vr_payment/status.html", extra_context={"status": "error"}
        ),
        name="status-error",
    ),
]
