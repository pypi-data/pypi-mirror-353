import requests


class MonoLookupError(Exception):
    pass


class MonoLookupClient:
    BASE_URL = "https://api.withmono.com"

    def __init__(self, sec_key: str):
        self.sec_key = sec_key
        self.session = requests.Session()
        self.session.headers.update({"mono-sec-key": self.sec_key})

    # --- BVN ---
    def initiate_bvn_lookup(self, data):
        url = f"{self.BASE_URL}/v2/lookup/bvn/initiate"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def verify_bvn_otp(self, data, session_id):
        url = f"{self.BASE_URL}/v2/lookup/bvn/verify"
        headers = {"x-session-id": session_id}
        resp = self.session.post(url, json=data, headers=headers)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def fetch_bvn_details(self, data, session_id):
        url = f"{self.BASE_URL}/v2/lookup/bvn/details"
        headers = {"x-session-id": session_id}
        resp = self.session.post(url, json=data, headers=headers)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- CAC ---
    def lookup_business(self, name):
        url = f"{self.BASE_URL}/v1/cac/lookup"
        resp = self.session.get(url, params={"name": name})
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def search_company(self, search):
        url = f"{self.BASE_URL}/v3/lookup/cac"
        resp = self.session.get(url, params={"search": search})
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def company_shareholders(self, company_id):
        url = f"{self.BASE_URL}/v3/lookup/cac/company/{company_id}"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def company_secretary(self, company_id):
        url = f"{self.BASE_URL}/v3/lookup/cac/company/{company_id}/secretary"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def company_directors(self, company_id):
        url = f"{self.BASE_URL}/v3/lookup/cac/company/{company_id}/directors"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def company_previous_address(self, company_id):
        url = f"{self.BASE_URL}/v3/lookup/cac/company/{company_id}/previous-address"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def company_change_of_name(self, company_id):
        url = f"{self.BASE_URL}/v3/lookup/cac/company/{company_id}/change-of-name"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- TIN ---
    def lookup_tin(self, data):
        url = f"{self.BASE_URL}/v3/lookup/tin"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- NIN ---
    def lookup_nin(self, data):
        url = f"{self.BASE_URL}/v3/lookup/nin"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Passport ---
    def lookup_passport(self, data):
        url = f"{self.BASE_URL}/v3/lookup/passport"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Driver's License ---
    def lookup_driver_license(self, data):
        url = f"{self.BASE_URL}/v3/lookup/driver_license"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Account Number ---
    def lookup_account_number(self, data):
        url = f"{self.BASE_URL}/v3/lookup/account-number"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Address Verification ---
    def verify_address(self, data):
        url = f"{self.BASE_URL}/v3/lookup/address"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Credit History ---
    def credit_history(self, provider, data):
        url = f"{self.BASE_URL}/v3/lookup/credit-history/{provider}"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Mashup ---
    def mashup(self, data):
        url = f"{self.BASE_URL}/v3/lookup/mashup"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Bank Listing (NIP) ---
    def bank_listing(self):
        url = f"{self.BASE_URL}/v3/lookup/banks"
        resp = self.session.post(url)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()
