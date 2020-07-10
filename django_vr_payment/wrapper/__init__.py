import requests
from requests import Response

from .checkout import CheckOutWrapper
from .transaction import TransactionWrapper
from .. import settings


class VRPaymentWrapper(TransactionWrapper, CheckOutWrapper):
    bearer_token = settings.VR_PAYMENT_BEARER_TOKEN
    entity_id = settings.VR_PAYMENT_ENTITY_ID
    sandbox = settings.VR_PAYMENT_SANDBOX
    url = (
        settings.VR_PAYMENT_TEST_URL
        if settings.VR_PAYMENT_SANDBOX
        else settings.VR_PAYMENT_LIVE_URL
    )

    def __init__(
        self, bearer_token: str = None, entity_id: str = None, sandbox: bool = None
    ) -> None:
        self.bearer_token = bearer_token if bearer_token else self.bearer_token
        self.entity_id = entity_id if entity_id else self.entity_id
        self.sandbox = sandbox if sandbox is not None else self.sandbox
        if self.sandbox:
            self.url = f"{settings.VR_PAYMENT_TEST_URL}"
        elif sandbox is not None:
            self.url = f"{settings.VR_PAYMENT_LIVE_URL}"
        super().__init__()

    def _call_api(
        self,
        url_append: str,
        method: str,
        data: dict = None,
        headers: dict = {},
        connect_timeout=2,
        read_timeout=10,
    ) -> Response:
        headers.update({"Authorization": f"Bearer {self.bearer_token}"})
        call_url = self.url + url_append
        try:
            if method is "POST":
                response = requests.post(
                    url=call_url,
                    headers=headers,
                    data=data,
                    timeout=(connect_timeout, read_timeout),
                )
            elif method is "GET":
                response = requests.get(
                    url=call_url,
                    headers=headers,
                    timeout=(connect_timeout, read_timeout),
                )
            else:
                raise NotImplementedError(f"method '{method}# is not supported")
        except requests.RequestException as e:
            raise e
        return response
