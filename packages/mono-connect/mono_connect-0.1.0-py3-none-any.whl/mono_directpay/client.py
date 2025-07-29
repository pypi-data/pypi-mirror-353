import requests


class MonoDirectpayError(Exception):
    pass


class MonoDirectpayClient:
    BASE_URL = "https://api.withmono.com"

    def __init__(self, sec_key: str):
        self.sec_key = sec_key
        self.session = requests.Session()
        self.session.headers.update({"mono-sec-key": self.sec_key})

    # --- One-time payments ---
    def initiate_payment(self, data):
        url = f"{self.BASE_URL}/v2/payments/initiate"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def verify_transaction(self, reference):
        url = f"{self.BASE_URL}/v2/payments/verify/{reference}"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def fetch_all_payments(self, **params):
        url = f"{self.BASE_URL}/v2/payments/transactions"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Mandates ---
    def get_banks(self):
        url = f"{self.BASE_URL}/v3/banks/list"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def create_mandate(self, data):
        url = f"{self.BASE_URL}/v3/payments/mandates"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def initiate_mandate(self, data):
        url = f"{self.BASE_URL}/v2/payments/initiate"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def mandate_status(self, mandate_id):
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/status"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def retrieve_mandate(self, mandate_id):
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def fetch_all_mandates(self, **params):
        url = f"{self.BASE_URL}/v3/payments/mandates"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def cancel_mandate(self, mandate_id):
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/cancel"
        resp = self.session.patch(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def pause_mandate(self, mandate_id):
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/pause"
        resp = self.session.patch(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def reinstate_mandate(self, mandate_id):
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/reinstate"
        resp = self.session.patch(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def verify_otp_mandate(self, data):
        url = f"{self.BASE_URL}/v3/payments/mandates/verify-otp"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Account actions ---
    def balance_inquiry(self, mandate_id, **params):
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/balance"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def debit_account(self, mandate_id, data):
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/debit"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def debit_account_beneficiary(self, mandate_id, data):
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/debit-beneficiary"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def retrieve_debit(self, mandate_id, debit_id):
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/debits/{debit_id}"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def retrieve_all_debits(self, mandate_id, **params):
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/debits"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()
