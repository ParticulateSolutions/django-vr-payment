Django VR Payment Copy + Pay
============================

Implementation of [VR Payment Copy + Pay](https://vr-pay-ecommerce.docs.oppwa.com/tutorials/integration-guide).
The following doc explain how to set up the VR Payment Copy + Pay base tutorial.

Quick start
-----------

1. Add "django_vr_payment" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django_vr_payment',
    ]

2. (optional) Include the vr-payment URLconf in your project urls.py like this::

    path('vr-payment/', include('django_vr_payment.urls')),

3. Run ``python manage.py migrate`` to create the vr-payment models.

4. Prepare a checkout:

    ```python
    from django_vr_payment.wrapper import VRPaymentWrapper

    vr_payment_wrapper = VRPaymentWrapper()
    basic_payment = vr_payment_wrapper.create_checkout(amount=<Decimal>, payment_type=<VRPaymentBasicPayment.PAYMENT_TYPE>, merchant_transaction_id=<UNIQUE_ID>)

    # the checkout_id for the VR Payment Copy&Pay form can be obtained through `checkout_id`
    checkout_id_for_forms = basic_payment.checkout_id
    ```

5. Pay via a payment form of your choice. A working example can be seen in `VRPaymentBasicCheckoutView`

6. Get the payment status:

    On return to `VR_PAYMENT_SHOPPER_RESULT_URL_NAME`, the app tries to get the status of a checkout object. You can also query VR Payment yourself:

    ```python
    from django_vr_payment.models import VRPaymentBasicPayment
    from django_vr_payment.wrapper import VRPaymentWrapper

    vr_payment_wrapper = VRPaymentWrapper()
    basic_payment = VRPaymentBasicPayment.objects.get(checkout_id=<CheckoutID>)

    # get 'initial' status querying the checkout api
    payment_status = vr_payment_wrapper.get_checkout_status(basic_payment)

    # or query transaction api either by vr_payment_checkout.payment_id or vr_payment_checkout.merchant_transaction_id
    payment_status = vr_payment_wrapper.get_transaction_by_merchant_transaction_id(basic_payment)
    ```

Copyright and license

Copyright 2020 Particulate Solutions GmbH, under MIT license.
