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

        Example:
            >>> client.initiate_bvn_lookup({"bvn": "12345678901"})
            {
                "status": "successful",
                "message": "BVN consent initiated successfully",
                "data": {
                    "session_id": "session_abcdef1234567890",
                    "expires_in": 300
                }
            }

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

        Example:
            >>> client.verify_bvn_otp({"otp": "123456"}, "session_abcdef1234567890")
            {
                "status": "successful",
                "message": "OTP verified successfully",
                "data": {
                    "verified": True
                }
            }

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

        Example:
            >>> client.fetch_bvn_details({}, "session_abcdef1234567890")
            {
                "status": "successful",
                "message": "BVN details retrieved successfully",
                "data": {
                    "bvn": "12345678901",
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone_number": "08012345678"
                }
            }

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

        Example:
            >>> client.lookup_business("John's Bakery")
            {
                "status": "successful",
                "message": "Business lookup successful",
                "data": {
                    "name": "John's Bakery",
                    "registration_number": "BN123456789",
                    "status": "Active"
                }
            }

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

        Example:
            >>> client.search_company("Bakery")
            {
                "status": "successful",
                "message": "Company search successful",
                "data": [
                    {
                        "name": "John's Bakery",
                        "registration_number": "BN123456789",
                        "status": "Active"
                    },
                    {
                        "name": "Doe's Bakery",
                        "registration_number": "BN987654321",
                        "status": "Inactive"
                    }
                ]
            }

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

        Example:
            >>> client.company_shareholders("company_abcdef1234567890")
            {
                "status": "successful",
                "message": "Shareholder information retrieved",
                "data": [
                    {
                        "name": "Jane Doe",
                        "percentage": 60
                    },
                    {
                        "name": "John Smith",
                        "percentage": 40
                    }
                ]
            }

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

        Example:
            >>> client.company_secretary("company_abcdef1234567890")
            {
                "status": "successful",
                "message": "Secretary information retrieved",
                "data": {
                    "name": "Mary Jane",
                    "phone_number": "08098765432",
                    "email": "mary.jane@example.com"
                }
            }

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

        Example:
            >>> client.company_directors("company_abcdef1234567890")
            {
                "status": "successful",
                "message": "Directors information retrieved",
                "data": [
                    {
                        "name": "Alice Johnson",
                        "position": "Managing Director"
                    },
                    {
                        "name": "Bob Brown",
                        "position": "Technical Director"
                    }
                ]
            }

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

        Example:
            >>> client.company_previous_address("company_abcdef1234567890")
            {
                "status": "successful",
                "message": "Previous address information retrieved",
                "data": {
                    "previous_address": "123 Old Street, Lagos",
                    "effective_date": "2020-01-01"
                }
            }

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

        Example:
            >>> client.company_change_of_name("company_abcdef1234567890")
            {
                "status": "successful",
                "message": "Change of name history retrieved",
                "data": [
                    {
                        "old_name": "Old Company Name",
                        "new_name": "New Company Name",
                        "effective_date": "2021-06-01"
                    }
                ]
            }

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

        Example:
            >>> client.lookup_tin({"tin": "1234567890"})
            {
                "status": "successful",
                "message": "TIN lookup successful",
                "data": {
                    "tin": "1234567890",
                    "name": "John Doe",
                    "business_name": "John's Bakery",
                    "address": "123 Bakery St, Lagos"
                }
            }

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

        Example:
            >>> client.lookup_nin({"nin": "12345678901"})
            {
                "status": "successful",
                "message": "NIN lookup successful",
                "data": {
                    "nin": "12345678901",
                    "name": "John Doe",
                    "date_of_birth": "1990-01-01",
                    "gender": "Male"
                }
            }

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

        Example:
            >>> client.lookup_passport({"passport_number": "A12345678"})
            {
                "status": "successful",
                "message": "Passport lookup successful",
                "data": {
                    "passport_number": "A12345678",
                    "name": "John Doe",
                    "nationality": "Nigerian",
                    "date_of_birth": "1990-01-01",
                    "sex": "Male"
                }
            }

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

        Example:
            >>> client.lookup_driver_license({"license_number": "D123456789"})
            {
                "status": "successful",
                "message": "Driver's license lookup successful",
                "data": {
                    "license_number": "D123456789",
                    "name": "John Doe",
                    "date_of_birth": "1990-01-01",
                    "sex": "Male",
                    "expiry_date": "2025-01-01"
                }
            }

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

        Example:
            >>> client.lookup_account_number({"account_number": "1234567890"})
            {
                "status": "successful",
                "message": "Account number lookup successful",
                "data": {
                    "account_number": "1234567890",
                    "bank": "Access Bank",
                    "bvn": "12345678901",
                    "account_name": "John Doe"
                }
            }

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

        Example:
            >>> client.verify_address({"meter_number": "123456", "house_address": "123 Main St"})
            {
                "status": "successful",
                "message": "Address verification successful",
                "data": {
                    "meter_number": "123456",
                    "house_address": "123 Main St",
                    "verified": True
                }
            }

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

        Example:
            >>> client.credit_history("crc", {"bvn": "12345678901"})
            {
                "status": "successful",
                "message": "Credit history retrieved",
                "data": {
                    "provider": "crc",
                    "bvn": "12345678901",
                    "credit_score": 750,
                    "credit_limit": 2000000
                }
            }

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

        Example:
            >>> client.mashup({"nin": "12345678901", "bvn": "12345678901", "dob": "1990-01-01"})
            {
                "status": "successful",
                "message": "Mashup verification successful",
                "data": {
                    "nin": "12345678901",
                    "bvn": "12345678901",
                    "dob": "1990-01-01",
                    "match": True
                }
            }

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

        Example:
            >>> client.bank_listing()
            {
                "status": "successful",
                "message": "Bank listing retrieved",
                "data": [
                    {
                        "code": "044",
                        "name": "Access Bank",
                        "type": "Commercial"
                    },
                    {
                        "code": "063",
                        "name": "Guaranty Trust Bank",
                        "type": "Commercial"
                    }
                ]
            }

        Reference:
            - POST /v3/lookup/banks
        """
        url = f"{self.BASE_URL}/v3/lookup/banks"
        resp = self.session.post(url)
        if not resp.ok:
            raise MonoLookupError(f"{resp.status_code}: {resp.text}")
        return resp.json()
