import requests


class MonoConnectError(Exception):
    pass


class MonoConnectClient:
    BASE_URL = "https://api.withmono.com"

    def __init__(self, sec_key: str):
        self.sec_key = sec_key
        self.session = requests.Session()
        self.session.headers.update({"mono-sec-key": self.sec_key})

    # --- Financial Data: Account ---
    def get_account_details(self, account_id):
        url = f"{self.BASE_URL}/v2/accounts/{account_id}"
        return self._get(url)

    def get_account_identity(self, account_id):
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/identity"
        return self._get(url)

    def unlink_account(self, account_id):
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/unlink"
        return self._post(url)

    def get_account_balance(self, account_id, realtime=True):
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/balance"
        headers = {"x-realtime": "true"} if realtime else {}
        return self._get(url, headers=headers)

    def get_creditworthiness(self, account_id, payload):
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/creditworthiness/"
        return self._post(url, json=payload)

    # --- Financial Data: Transactions ---
    def get_transactions(self, account_id, **params):
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/transactions"
        return self._get(url, params=params)

    # --- Financial Data: Investments ---
    def get_account_earnings(self, account_id):
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/earnings"
        return self._get(url)

    def get_account_assets(self, account_id):
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/assets"
        return self._get(url)

    # --- Authorisation ---
    def initiate_account_linking(self, payload):
        url = f"{self.BASE_URL}/v2/accounts/initiate"
        return self._post(url, json=payload)

    def initiate_account_reauth(self, payload):
        url = f"{self.BASE_URL}/v2/accounts/initiate"
        return self._post(url, json=payload)

    def token_exchange(self, code):
        url = f"{self.BASE_URL}/v2/accounts/auth"
        return self._post(url, json={"code": code})

    # --- Statement ---
    def get_account_statement(self, account_id, **params):
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/statement"
        return self._get(url, params=params)

    def get_account_statement_job(self, account_id, job_id):
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/statement/jobs/{job_id}"
        return self._get(url)

    # --- Data Enrichment ---
    def categorise_transactions(self, account_id):
        url = f"{self.BASE_URL}/v1/enrichments/{account_id}/transaction-categorisation"
        return self._get(url)

    def categorise_transactions_csv(self, file_path):
        url = f"{self.BASE_URL}/v2/enrichments/transaction-categorisation"
        files = {"transactions": open(file_path, "rb")}
        return self._post(url, files=files)

    def get_categorisation_records(self):
        url = f"{self.BASE_URL}/v1/enrichments/transaction-categorisation/records"
        return self._get(url)

    def enrich_transaction_metadata(self, account_id):
        url = f"{self.BASE_URL}/v1/enrichments/{account_id}/transaction-metadata"
        return self._get(url)

    def enrich_transaction_metadata_csv(self, file_path):
        url = f"{self.BASE_URL}/v2/enrichments/transaction-metadata"
        files = {"transactions": open(file_path, "rb")}
        return self._post(url, files=files)

    def get_metadata_records(self):
        url = f"{self.BASE_URL}/v1/enrichments/transaction-metadata/records"
        return self._get(url)

    def get_statement_insights(self, account_id):
        url = f"{self.BASE_URL}/v2/enrichments/{account_id}/statement-insights"
        return self._get(url)

    def get_statement_insight_records(self, account_id):
        url = f"{self.BASE_URL}/v1/enrichments/{account_id}/statement-insights/records"
        return self._get(url)

    # --- Internal helpers ---
    def _get(self, url, params=None, headers=None):
        h = self.session.headers.copy()
        if headers:
            h.update(headers)
        resp = self.session.get(url, params=params, headers=h)
        if not resp.ok:
            raise MonoConnectError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def _post(self, url, json=None, files=None, headers=None):
        h = self.session.headers.copy()
        if headers:
            h.update(headers)
        resp = self.session.post(url, json=json, files=files, headers=h)
        if not resp.ok:
            raise MonoConnectError(f"{resp.status_code}: {resp.text}")
        return resp.json()
