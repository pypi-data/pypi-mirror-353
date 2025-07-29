"""
mono_directpay.client
---------------------
Python SDK client for Mono Directpay APIs.
Provides methods for payments, mandates, and account actions.
"""

import requests


class MonoDirectpayError(Exception):
    """Custom exception for Mono Directpay SDK errors."""

    pass


class MonoDirectpayClient:
    """
    Client for interacting with the Mono Directpay API.

    Args:
        sec_key (str): Your Mono secret key.
    """

    BASE_URL = "https://api.withmono.com"

    def __init__(self, sec_key: str):
        """
        Initialize the MonoDirectpayClient.

        Args:
            sec_key (str): Your Mono secret key.
        """
        self.sec_key = sec_key
        self.session = requests.Session()
        self.session.headers.update({"mono-sec-key": self.sec_key})

    # --- One-time payments ---
    def initiate_payment(self, data):
        """
        Initiate a one-time payment.

        Args:
            data (dict): Payment initiation payload.

        Returns:
            dict: Payment initiation response.
        """
        url = f"{self.BASE_URL}/v2/payments/initiate"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def verify_transaction(self, reference):
        """
        Verify a payment transaction.

        Args:
            reference (str): Transaction reference.

        Returns:
            dict: Verification response.
        """
        url = f"{self.BASE_URL}/v2/payments/verify/{reference}"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def fetch_all_payments(self, **params):
        """
        Fetch all payment transactions.

        Args:
            **params: Optional query parameters.

        Returns:
            dict: Payments data.
        """
        url = f"{self.BASE_URL}/v2/payments/transactions"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Mandates ---
    def get_banks(self):
        """
        Retrieve a list of supported banks.

        Returns:
            dict: Banks data.
        """
        url = f"{self.BASE_URL}/v3/banks/list"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def create_mandate(self, data):
        """
        Create a new payment mandate.

        Args:
            data (dict): Mandate creation payload.

        Returns:
            dict: Mandate creation response.
        """
        url = f"{self.BASE_URL}/v3/payments/mandates"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def initiate_mandate(self, data):
        """
        Initiate a payment mandate.

        Args:
            data (dict): Mandate initiation payload.

        Returns:
            dict: Mandate initiation response.
        """
        url = f"{self.BASE_URL}/v2/payments/initiate"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def mandate_status(self, mandate_id):
        """
        Retrieve the status of a mandate.

        Args:
            mandate_id (str): The mandate ID.

        Returns:
            dict: Mandate status.
        """
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/status"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def retrieve_mandate(self, mandate_id):
        """
        Retrieve details of a specific mandate.

        Args:
            mandate_id (str): The mandate ID.

        Returns:
            dict: Mandate details.
        """
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def fetch_all_mandates(self, **params):
        """
        Fetch all mandates.

        Args:
            **params: Optional query parameters.

        Returns:
            dict: Mandates data.
        """
        url = f"{self.BASE_URL}/v3/payments/mandates"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def cancel_mandate(self, mandate_id):
        """
        Cancel a mandate.

        Args:
            mandate_id (str): The mandate ID.

        Returns:
            dict: Cancel response.
        """
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/cancel"
        resp = self.session.patch(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def pause_mandate(self, mandate_id):
        """
        Pause a mandate.

        Args:
            mandate_id (str): The mandate ID.

        Returns:
            dict: Pause response.
        """
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/pause"
        resp = self.session.patch(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def reinstate_mandate(self, mandate_id):
        """
        Reinstate a paused mandate.

        Args:
            mandate_id (str): The mandate ID.

        Returns:
            dict: Reinstate response.
        """
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/reinstate"
        resp = self.session.patch(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def verify_otp_mandate(self, data):
        """
        Verify OTP for a mandate.

        Args:
            data (dict): OTP verification payload.

        Returns:
            dict: OTP verification response.
        """
        url = f"{self.BASE_URL}/v3/payments/mandates/verify-otp"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    # --- Account actions ---
    def balance_inquiry(self, mandate_id, **params):
        """
        Retrieve the balance for a mandate.

        Args:
            mandate_id (str): The mandate ID.
            **params: Optional query parameters.

        Returns:
            dict: Balance data.
        """
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/balance"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def debit_account(self, mandate_id, data):
        """
        Debit an account using a mandate.

        Args:
            mandate_id (str): The mandate ID.
            data (dict): Debit payload.

        Returns:
            dict: Debit response.
        """
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/debit"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def debit_account_beneficiary(self, mandate_id, data):
        """
        Debit a beneficiary account using a mandate.

        Args:
            mandate_id (str): The mandate ID.
            data (dict): Debit payload.

        Returns:
            dict: Debit response.
        """
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/debit-beneficiary"
        resp = self.session.post(url, json=data)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def retrieve_debit(self, mandate_id, debit_id):
        """
        Retrieve details of a specific debit transaction.

        Args:
            mandate_id (str): The mandate ID.
            debit_id (str): The debit transaction ID.

        Returns:
            dict: Debit details.
        """
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/debits/{debit_id}"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def retrieve_all_debits(self, mandate_id, **params):
        """
        Retrieve all debit transactions for a mandate.

        Args:
            mandate_id (str): The mandate ID.
            **params: Optional query parameters.

        Returns:
            dict: Debits data.
        """
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/debits"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()
