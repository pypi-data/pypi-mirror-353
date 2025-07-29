"""
mono_lookup.client
------------------
Python SDK client for Mono Lookup APIs.
Provides methods for identity, business, and document verification.
"""

import requests


class MonoLookupError(Exception):
    """Custom exception for Mono Lookup SDK errors."""

    pass


class MonoLookupClient:
    """
    Client for interacting with the Mono Lookup API.

    Args:
        sec_key (str): Your Mono secret key.
    """

    BASE_URL = "https://api.withmono.com"

    def __init__(self, sec_key: str):
        """
        Initialize the MonoLookupClient.

        Args:
            sec_key (str): Your Mono secret key.
        """
        self.sec_key = sec_key
        self.session = requests.Session()
        self.session.headers.update({"mono-sec-key": self.sec_key})

    # --- BVN ---
    def initiate_bvn_lookup(self, data):
        """
        Initiate a BVN consent request.

        Args:
            data (dict): BVN lookup payload.

        Returns:
            dict: BVN lookup response.

        Reference:
            - POST /v2/lookup/bvn/initiate
        """
        url = f"{self.BASE_URL}/v2/lookup/bvn/initiate"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def verify_bvn_otp(self, data, session_id):
        """
        Verify BVN request via OTP.

        Args:
            data (dict): OTP verification payload.
            session_id (str): Session ID from BVN lookup.

        Returns:
            dict: OTP verification response.

        Reference:
            - POST /v2/lookup/bvn/verify
        """
        url = f"{self.BASE_URL}/v2/lookup/bvn/verify"
        headers = {"x-session-id": session_id}
        resp = self.session.post(url, json=data, headers=headers)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def fetch_bvn_details(self, data, session_id):
        """
        Retrieve BVN information after verification.

        Args:
            data (dict): BVN details payload.
            session_id (str): Session ID from BVN lookup.

        Returns:
            dict: BVN details.

        Reference:
            - POST /v2/lookup/bvn/details
        """
        url = f"{self.BASE_URL}/v2/lookup/bvn/details"
        headers = {"x-session-id": session_id}
        resp = self.session.post(url, json=data, headers=headers)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- CAC ---
    def lookup_business(self, name):
        """
        Lookup a business by name.

        Args:
            name (str): Business name.

        Returns:
            dict: Business lookup result.

        Reference:
            - GET /v1/cac/lookup
        """
        url = f"{self.BASE_URL}/v1/cac/lookup"
        resp = self.session.get(url, params={"name": name})
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def search_company(self, search):
        """
        Search for a company by keyword.

        Args:
            search (str): Search keyword.

        Returns:
            dict: Company search result.

        Reference:
            - GET /v3/lookup/cac
        """
        url = f"{self.BASE_URL}/v3/lookup/cac"
        resp = self.session.get(url, params={"search": search})
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def company_shareholders(self, company_id):
        """
        Retrieve shareholder information for a company.

        Args:
            company_id (str): Company ID.

        Returns:
            dict: Shareholder information.

        Reference:
            - GET /v3/lookup/cac/company/{company_id}
        """
        url = f"{self.BASE_URL}/v3/lookup/cac/company/{company_id}"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def company_secretary(self, company_id):
        """
        Retrieve secretary information for a company.

        Args:
            company_id (str): Company ID.

        Returns:
            dict: Secretary information.

        Reference:
            - GET /v3/lookup/cac/company/{company_id}/secretary
        """
        url = f"{self.BASE_URL}/v3/lookup/cac/company/{company_id}/secretary"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def company_directors(self, company_id):
        """
        Retrieve directors information for a company.

        Args:
            company_id (str): Company ID.

        Returns:
            dict: Directors information.

        Reference:
            - GET /v3/lookup/cac/company/{company_id}/directors
        """
        url = f"{self.BASE_URL}/v3/lookup/cac/company/{company_id}/directors"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def company_previous_address(self, company_id):
        """
        Retrieve previous address information for a company.

        Args:
            company_id (str): Company ID.

        Returns:
            dict: Previous address information.

        Reference:
            - GET /v3/lookup/cac/company/{company_id}/previous-address
        """
        url = f"{self.BASE_URL}/v3/lookup/cac/company/{company_id}/previous-address"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def company_change_of_name(self, company_id):
        """
        Retrieve change of name history for a company.

        Args:
            company_id (str): Company ID.

        Returns:
            dict: Change of name history.

        Reference:
            - GET /v3/lookup/cac/company/{company_id}/change-of-name
        """
        url = f"{self.BASE_URL}/v3/lookup/cac/company/{company_id}/change-of-name"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- TIN ---
    def lookup_tin(self, data):
        """
        Verify the tax identification number (TIN) of an entity.

        Args:
            data (dict): TIN lookup payload.

        Returns:
            dict: TIN lookup result.

        Reference:
            - POST /v3/lookup/tin
        """
        url = f"{self.BASE_URL}/v3/lookup/tin"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- NIN ---
    def lookup_nin(self, data):
        """
        Verify the national identification number (NIN) of a user.

        Args:
            data (dict): NIN lookup payload.

        Returns:
            dict: NIN lookup result.

        Reference:
            - POST /v3/lookup/nin
        """
        url = f"{self.BASE_URL}/v3/lookup/nin"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Passport ---
    def lookup_passport(self, data):
        """
        Verify an international passport document.

        Args:
            data (dict): Passport lookup payload.

        Returns:
            dict: Passport lookup result.

        Reference:
            - POST /v3/lookup/passport
        """
        url = f"{self.BASE_URL}/v3/lookup/passport"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Driver's License ---
    def lookup_driver_license(self, data):
        """
        Verify a driver's license number.

        Args:
            data (dict): Driver's license lookup payload.

        Returns:
            dict: Driver's license lookup result.

        Reference:
            - POST /v3/lookup/driver_license
        """
        url = f"{self.BASE_URL}/v3/lookup/driver_license"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Account Number ---
    def lookup_account_number(self, data):
        """
        Verify an account number and return the masked BVN attached.

        Args:
            data (dict): Account number lookup payload.

        Returns:
            dict: Account number lookup result.

        Reference:
            - POST /v3/lookup/account-number
        """
        url = f"{self.BASE_URL}/v3/lookup/account-number"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Address Verification ---
    def verify_address(self, data):
        """
        Verify an address via meter number and house address.

        Args:
            data (dict): Address verification payload.

        Returns:
            dict: Address verification result.

        Reference:
            - POST /v3/lookup/address
        """
        url = f"{self.BASE_URL}/v3/lookup/address"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Credit History ---
    def credit_history(self, provider, data):
        """
        Retrieve a user's credit history from a specified provider.

        Args:
            provider (str): Provider name (e.g., 'crc', 'xds', 'all').
            data (dict): Credit history payload.

        Returns:
            dict: Credit history result.

        Reference:
            - POST /v3/lookup/credit-history/{provider}
        """
        url = f"{self.BASE_URL}/v3/lookup/credit-history/{provider}"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Mashup ---
    def mashup(self, data):
        """
        Verify NIN, BVN, and date of birth in one API call for KYC.

        Args:
            data (dict): Mashup payload.

        Returns:
            dict: Mashup result.

        Reference:
            - POST /v3/lookup/mashup
        """
        url = f"{self.BASE_URL}/v3/lookup/mashup"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Bank Listing (NIP) ---
    def bank_listing(self):
        """
        Retrieve NIP supported bank coverage.

        Returns:
            dict: Bank listing result.

        Reference:
            - POST /v3/lookup/banks
        """
        url = f"{self.BASE_URL}/v3/lookup/banks"
        resp = self.session.post(url)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()
