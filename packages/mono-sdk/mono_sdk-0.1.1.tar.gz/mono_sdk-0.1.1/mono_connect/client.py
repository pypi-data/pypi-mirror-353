"""
mono_connect.client
-------------------
Python SDK client for Mono Connect APIs.
Provides methods for retrieving financial data, account management, authorisation, statements, and data enrichment.
"""

import requests


class MonoConnectError(Exception):
    """Custom exception for Mono Connect SDK errors."""

    pass


class MonoConnectClient:
    """
    Client for interacting with the Mono Connect API.

    Args:
        sec_key (str): Your Mono secret key.
    """

    BASE_URL = "https://api.withmono.com"

    def __init__(self, sec_key: str):
        """
        Initialize the MonoConnectClient.

        Args:
            sec_key (str): Your Mono secret key.
        """
        self.sec_key = sec_key
        self.session = requests.Session()
        self.session.headers.update({"mono-sec-key": self.sec_key})

    # --- Financial Data: Account ---
    def get_account_details(self, account_id):
        """
        Retrieve details of a specific account.

        Args:
            account_id (str): The account ID.

        Returns:
            dict: Account details.
        """
        url = f"{self.BASE_URL}/v2/accounts/{account_id}"
        return self._get(url)

    def get_account_identity(self, account_id):
        """
        Retrieve identity information associated with a specific account.

        Args:
            account_id (str): The account ID.

        Returns:
            dict: Identity information.
        """
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/identity"
        return self._get(url)

    def unlink_account(self, account_id):
        """
        Unlink a financial account.

        Args:
            account_id (str): The account ID.

        Returns:
            dict: Unlink response.
        """
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/unlink"
        return self._post(url)

    def get_account_balance(self, account_id, realtime=True):
        """
        Retrieve the balance of a specific account.

        Args:
            account_id (str): The account ID.
            realtime (bool): Whether to fetch real-time balance.

        Returns:
            dict: Account balance.
        """
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/balance"
        headers = {"x-realtime": "true"} if realtime else {}
        return self._get(url, headers=headers)

    def get_creditworthiness(self, account_id, payload):
        """
        Retrieve the creditworthiness of a user.

        Args:
            account_id (str): The account ID.
            payload (dict): Creditworthiness request payload.

        Returns:
            dict: Creditworthiness response.
        """
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/creditworthiness/"
        return self._post(url, json=payload)

    # --- Financial Data: Transactions ---
    def get_transactions(self, account_id, **params):
        """
        Retrieve transactions for a specific account.

        Args:
            account_id (str): The account ID.
            **params: Optional query parameters.

        Returns:
            dict: Transactions data.
        """
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/transactions"
        return self._get(url, params=params)

    # --- Financial Data: Investments ---
    def get_account_earnings(self, account_id):
        """
        Retrieve earnings for a specific investment account.

        Args:
            account_id (str): The account ID.

        Returns:
            dict: Earnings data.
        """
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/earnings"
        return self._get(url)

    def get_account_assets(self, account_id):
        """
        Retrieve assets for a specific investment account.

        Args:
            account_id (str): The account ID.

        Returns:
            dict: Assets data.
        """
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/assets"
        return self._get(url)

    # --- Authorisation ---
    def initiate_account_linking(self, payload):
        """
        Initiate linking of an account.

        Args:
            payload (dict): Account linking request payload.

        Returns:
            dict: Linking response.
        """
        url = f"{self.BASE_URL}/v2/accounts/initiate"
        return self._post(url, json=payload)

    def initiate_account_reauth(self, payload):
        """
        Initiate reauthorization of a previously linked account.

        Args:
            payload (dict): Reauthorization request payload.

        Returns:
            dict: Reauthorization response.
        """
        url = f"{self.BASE_URL}/v2/accounts/initiate"
        return self._post(url, json=payload)

    def token_exchange(self, code):
        """
        Exchange a code for an account ID after successful enrolment.

        Args:
            code (str): The code returned from the Mono Connect widget.

        Returns:
            dict: Token exchange response.
        """
        url = f"{self.BASE_URL}/v2/accounts/auth"
        return self._post(url, json={"code": code})

    # --- Statement ---
    def get_account_statement(self, account_id, **params):
        """
        Retrieve the bank statement for a connected financial account.

        Args:
            account_id (str): The account ID.
            **params: Optional query parameters.

        Returns:
            dict: Statement data.
        """
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/statement"
        return self._get(url, params=params)

    def get_account_statement_job(self, account_id, job_id):
        """
        Retrieve the status of a statement generation job.

        Args:
            account_id (str): The account ID.
            job_id (str): The job ID.

        Returns:
            dict: Statement job status.
        """
        url = f"{self.BASE_URL}/v2/accounts/{account_id}/statement/jobs/{job_id}"
        return self._get(url)

    # --- Data Enrichment ---
    def categorise_transactions(self, account_id):
        """
        Categorise transactions for a specific account.

        Args:
            account_id (str): The account ID.

        Returns:
            dict: Categorisation response.
        """
        url = f"{self.BASE_URL}/v1/enrichments/{account_id}/transaction-categorisation"
        return self._get(url)

    def categorise_transactions_csv(self, file_path):
        """
        Categorise transactions by uploading a CSV file.

        Args:
            file_path (str): Path to the CSV file.

        Returns:
            dict: Categorisation response.
        """
        url = f"{self.BASE_URL}/v2/enrichments/transaction-categorisation"
        files = {"transactions": open(file_path, "rb")}
        return self._post(url, files=files)

    def get_categorisation_records(self):
        """
        Retrieve all records of categorised transactions uploaded for the app.

        Returns:
            dict: Categorisation records.
        """
        url = f"{self.BASE_URL}/v1/enrichments/transaction-categorisation/records"
        return self._get(url)

    def enrich_transaction_metadata(self, account_id):
        """
        Enrich transaction metadata for a specific account.

        Args:
            account_id (str): The account ID.

        Returns:
            dict: Metadata enrichment response.
        """
        url = f"{self.BASE_URL}/v1/enrichments/{account_id}/transaction-metadata"
        return self._get(url)

    def enrich_transaction_metadata_csv(self, file_path):
        """
        Enrich transaction metadata by uploading a CSV file.

        Args:
            file_path (str): Path to the CSV file.

        Returns:
            dict: Metadata enrichment response.
        """
        url = f"{self.BASE_URL}/v2/enrichments/transaction-metadata"
        files = {"transactions": open(file_path, "rb")}
        return self._post(url, files=files)

    def get_metadata_records(self):
        """
        Retrieve all records of transaction metadata uploaded for the app.

        Returns:
            dict: Metadata records.
        """
        url = f"{self.BASE_URL}/v1/enrichments/transaction-metadata/records"
        return self._get(url)

    def get_statement_insights(self, account_id):
        """
        Retrieve statement insights for a specific account.

        Args:
            account_id (str): The account ID.

        Returns:
            dict: Statement insights.
        """
        url = f"{self.BASE_URL}/v2/enrichments/{account_id}/statement-insights"
        return self._get(url)

    def get_statement_insight_records(self, account_id):
        """
        Retrieve statement insight records for a specific account.

        Args:
            account_id (str): The account ID.

        Returns:
            dict: Statement insight records.
        """
        url = f"{self.BASE_URL}/v1/enrichments/{account_id}/statement-insights/records"
        return self._get(url)

    # --- Internal helpers ---
    def _get(self, url, params=None, headers=None):
        """
        Internal helper for HTTP GET requests.

        Args:
            url (str): The request URL.
            params (dict, optional): Query parameters.
            headers (dict, optional): Additional headers.

        Returns:
            dict: JSON response.

        Raises:
            MonoConnectError: If the request fails.
        """
        h = self.session.headers.copy()
        if headers:
            h.update(headers)
        resp = self.session.get(url, params=params, headers=h)
        if not resp.ok:
            raise MonoConnectError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def _post(self, url, json=None, files=None, headers=None):
        """
        Internal helper for HTTP POST requests.

        Args:
            url (str): The request URL.
            json (dict, optional): JSON payload.
            files (dict, optional): Files to upload.
            headers (dict, optional): Additional headers.

        Returns:
            dict: JSON response.

        Raises:
            MonoConnectError: If the request fails.
        """
        h = self.session.headers.copy()
        if headers:
            h.update(headers)
        resp = self.session.post(url, json=json, files=files, headers=h)
        if not resp.ok:
            raise MonoConnectError(f"{resp.status_code}: {resp.text}")
        return resp.json()
