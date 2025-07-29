import requests


class MonoCustomerError(Exception):
    pass


class MonoCustomerClient:
    BASE_URL = "https://api.withmono.com"

    def __init__(self, sec_key: str):
        self.sec_key = sec_key
        self.session = requests.Session()
        self.session.headers.update({"mono-sec-key": self.sec_key})

    def create_customer(self, data):
        url = f"{self.BASE_URL}/v2/customers"
        resp = self.session.post(url, json=data)
        if resp.status_code not in (200, 201):
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def retrieve_customer(self, customer_id):
        url = f"{self.BASE_URL}/v2/customers/{customer_id}"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def list_customers(self, **params):
        url = f"{self.BASE_URL}/v2/customers"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def update_customer(self, customer_id, data):
        url = f"{self.BASE_URL}/v2/customers/{customer_id}"
        resp = self.session.patch(url, json=data)
        if not resp.ok:
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def delete_customer(self, customer_id):
        url = f"{self.BASE_URL}/v2/customers/{customer_id}"
        resp = self.session.delete(url)
        if not resp.ok:
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def get_customer_transactions(self, customer_id, **params):
        url = f"{self.BASE_URL}/customers/{customer_id}/transactions"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def fetch_linked_accounts(self, **params):
        url = f"{self.BASE_URL}/v2/accounts"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()
