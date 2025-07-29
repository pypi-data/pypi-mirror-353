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

        Example:
            >>> client.get_account_details("659d61857baef05dd147fd8f")
            {
                "status": "successful",
                "message": "Request was succesfully completed",
                "timestamp": "2025-01-11T19:35:57.968Z",
                "data": {
                    "account": {
                        "id": "659d61857baef05dd147fd8f",
                        "name": "Samuel Olamide",
                        "currency": "NGN",
                        "type": "savings_account",
                        "account_number": "0131883461",
                        "balance": 100000,
                        "institution": {
                            "name": "ALAT by WEMA",
                            "bank_code": "035",
                            "type": "PERSONAL_BANKING"
                        },
                        "bvn": null
                    },
                    "customer": {
                        "id": "659d611c7baef05dd147ed1d"
                    },
                    "meta": {
                        "data_status": "AVAILABLE",
                        "auth_method": "internet_banking"
                    }
                }
            }
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

        Example:
            >>> client.get_account_identity("account_id")
            {
                "status": "successful",
                "message": "Request was succesfully completed",
                "timestamp": "2025-01-11T20:41:29.009Z",
                "data": {
                    "full_name": "OJO DANIEL",
                    "email": "email@yahoo.com",
                    "phone": "08060000000",
                    "gender": null,
                    "bvn": "11111111000",
                    "marital_status": null,
                    "address_line1": "VICARAGE IYERU",
                    "address_line2": "CHRCH",
                    "created_at": "2021-04-29T09:46:49.641Z",
                    "updated_at": "2021-04-29T09:46:49.641Z"
                }
            }
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

        Example:
            >>> client.unlink_account("account_id")
            {
                "status": "successful",
                "message": "Request was succesfully completed",
                "timestamp": "2025-01-11T20:38:12.065Z"
            }
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

        Example:
            >>> client.get_account_balance("6782d72b5874ebd700f01af4")
            {
                "status": "successful",
                "message": "Request was succesfully completed",
                "timestamp": "2025-01-11T20:51:43.326Z",
                "data": {
                    "id": "6782d72b5874ebd700f01af4",
                    "name": "Samuel Olamide",
                    "account_number": "0131883461",
                    "balance": 10000000,
                    "currency": "NGN"
                }
            }
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

        Example:
            >>> client.get_creditworthiness("account_id", {
            ...     "bvn": "12345678901",
            ...     "principal": 30000000,
            ...     "interest_rate": 5,
            ...     "term": 12,
            ...     "run_credit_check": True
            ... })
            {
                "status": "successful",
                "message": "The creditworthiness of Samuel Olumide is currently being processed. Once completed, the data will be sent to your webhook.",
                "timestamp": "2025-01-11T21:13:01.006Z",
                "data": null
            }
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

        Example:
            >>> client.get_transactions("6782d72b5874ebd700f01af4", narration="Uber transactions", type="debit", paginate=True, limit=55)
            {
                "status": "successful",
                "message": "No transactions found for the provided date filter, please try again with different date",
                "timestamp": "2025-01-11T21:37:45.248Z",
                "data": null,
                "meta": null
            }
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

        Example:
            >>> client.get_account_earnings("65f883fbdd5cd948a675bc4a")
            {
                "status": "successful",
                "message": "Request was succesfully completed",
                "timestamp": "2024-03-15T15:09:13.581Z",
                "data": [
                    {
                        "id": "65d7667c27d138f56c4977d0",
                        "amount": 1071,
                        "narration": "Transfer to Wallet from Mrchemicalmusic plan",
                        "date": "2024-02-13T17:24:30.000Z",
                        "asset": {
                            "symbol": null,
                            "name": "Mrchemicalmusic",
                            "sale_price": null,
                            "quantity_sold": null
                        }
                    }
                ]
            }
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

        Example:
            >>> client.get_account_assets("65f8899d64b5baaa044c651a")
            {
                "status": "successful",
                "message": "Request was succesfully completed",
                "timestamp": "2024-03-15T15:10:57.842Z",
                "data": {
                    "id": "65d7667c27d138f56c4977cf",
                    "balances": {"_u_s_d": 0},
                    "assets": [
                        {
                            "name": "Mrchemicalmusic",
                            "type": "Mixed",
                            "cost": 1071,
                            "return": 1071,
                            "quantity": null,
                            "currency": "USD",
                            "details": {
                                "symbol": null,
                                "price": null,
                                "current_balance": 0
                            }
                        }
                    ]
                }
            }
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

        Example:
            >>> client.initiate_account_linking({
            ...     "account_number": "0131883461",
            ...     "bank_code": "035",
            ...     "bvn": "12345678901",
            ...     "email": "samuel@example.com",
            ...     "phone": "08060000000"
            ... })
            {
                "status": "successful",
                "message": "Account linking initiated. Please complete the process via the provided link.",
                "timestamp": "2025-01-11T21:45:00.000Z",
                "data": {
                    "link": "https://widget.withmono.com/?token=eyJhbGciOiJIUzI1NiIsInR..."
                }
            }
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

        Example:
            >>> client.initiate_account_reauth({
            ...     "account_number": "0131883461",
            ...     "bank_code": "035",
            ...     "bvn": "12345678901",
            ...     "email": "samuel@example.com",
            ...     "phone": "08060000000"
            ... })
            {
                "status": "successful",
                "message": "Account reauthorization initiated. Please complete the process via the provided link.",
                "timestamp": "2025-01-11T21:46:00.000Z",
                "data": {
                    "link": "https://widget.withmono.com/?token=eyJhbGciOiJIUzI1NiIsInR..."
                }
            }
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

        Example:
            >>> client.token_exchange("authorization_code_from_mono")
            {
                "status": "successful",
                "message": "Token exchange successful.",
                "timestamp": "2025-01-11T21:47:00.000Z",
                "data": {
                    "account_id": "659d61857baef05dd147fd8f",
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR..."
                }
            }
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

        Example:
            >>> client.get_account_statement("account_id", from_date="2025-01-01", to_date="2025-01-31")
            {
                "status": "successful",
                "message": "Request was succesfully completed",
                "timestamp": "2025-01-11T21:48:00.000Z",
                "data": {
                    "id": "statement_id",
                    "account_id": "659d61857baef05dd147fd8f",
                    "from_date": "2025-01-01",
                    "to_date": "2025-01-31",
                    "generated_at": "2025-01-11T21:48:00.000Z",
                    "file_url": "https://api.withmono.com/v2/accounts/659d61857baef05dd147fd8f/statement/statement_id"
                }
            }
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

        Example:
            >>> client.get_account_statement_job("account_id", "job_id")
            {
                "status": "successful",
                "message": "Request was succesfully completed",
                "timestamp": "2025-01-11T21:49:00.000Z",
                "data": {
                    "id": "job_id",
                    "account_id": "659d61857baef05dd147fd8f",
                    "status": "completed",
                    "created_at": "2025-01-11T21:48:00.000Z",
                    "completed_at": "2025-01-11T21:49:00.000Z",
                    "file_url": "https://api.withmono.com/v2/accounts/659d61857baef05dd147fd8f/statement/statement_id"
                }
            }
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

        Example:
            >>> client.categorise_transactions("account_id")
            {
                "status": "successful",
                "message": "Request was succesfully completed",
                "timestamp": "2025-01-11T21:50:00.000Z",
                "data": {
                    "id": "categorisation_id",
                    "account_id": "659d61857baef05dd147fd8f",
                    "status": "completed",
                    "created_at": "2025-01-11T21:50:00.000Z",
                    "updated_at": "2025-01-11T21:50:00.000Z"
                }
            }
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

        Example:
            >>> client.categorise_transactions_csv("/path/to/transactions.csv")
            {
                "status": "successful",
                "message": "Transactions categorised successfully.",
                "timestamp": "2025-01-11T21:51:00.000Z",
                "data": {
                    "id": "categorisation_id",
                    "account_id": "659d61857baef05dd147fd8f",
                    "status": "completed",
                    "created_at": "2025-01-11T21:51:00.000Z",
                    "updated_at": "2025-01-11T21:51:00.000Z"
                }
            }
        """
        url = f"{self.BASE_URL}/v2/enrichments/transaction-categorisation"
        files = {"transactions": open(file_path, "rb")}
        return self._post(url, files=files)

    def get_categorisation_records(self):
        """
        Retrieve all records of categorised transactions uploaded for the app.

        Returns:
            dict: Categorisation records.

        Example:
            >>> client.get_categorisation_records()
            {
                "status": "successful",
                "message": "Request was succesfully completed",
                "timestamp": "2025-01-11T21:52:00.000Z",
                "data": [
                    {
                        "id": "categorisation_id",
                        "account_id": "659d61857baef05dd147fd8f",
                        "status": "completed",
                        "created_at": "2025-01-11T21:50:00.000Z",
                        "updated_at": "2025-01-11T21:50:00.000Z"
                    }
                ]
            }
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

        Example:
            >>> client.enrich_transaction_metadata("account_id")
            {
                "status": "successful",
                "message": "Request was succesfully completed",
                "timestamp": "2025-01-11T21:53:00.000Z",
                "data": {
                    "id": "metadata_id",
                    "account_id": "659d61857baef05dd147fd8f",
                    "status": "completed",
                    "created_at": "2025-01-11T21:53:00.000Z",
                    "updated_at": "2025-01-11T21:53:00.000Z"
                }
            }
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

        Example:
            >>> client.enrich_transaction_metadata_csv("/path/to/transactions_metadata.csv")
            {
                "status": "successful",
                "message": "Transaction metadata enriched successfully.",
                "timestamp": "2025-01-11T21:54:00.000Z",
                "data": {
                    "id": "metadata_id",
                    "account_id": "659d61857baef05dd147fd8f",
                    "status": "completed",
                    "created_at": "2025-01-11T21:54:00.000Z",
                    "updated_at": "2025-01-11T21:54:00.000Z"
                }
            }
        """
        url = f"{self.BASE_URL}/v2/enrichments/transaction-metadata"
        files = {"transactions": open(file_path, "rb")}
        return self._post(url, files=files)

    def get_metadata_records(self):
        """
        Retrieve all records of transaction metadata uploaded for the app.

        Returns:
            dict: Metadata records.

        Example:
            >>> client.get_metadata_records()
            {
                "status": "successful",
                "message": "Request was succesfully completed",
                "timestamp": "2025-01-11T21:55:00.000Z",
                "data": [
                    {
                        "id": "metadata_id",
                        "account_id": "659d61857baef05dd147fd8f",
                        "status": "completed",
                        "created_at": "2025-01-11T21:53:00.000Z",
                        "updated_at": "2025-01-11T21:53:00.000Z"
                    }
                ]
            }
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

        Example:
            >>> client.get_statement_insights("account_id")
            {
                "status": "successful",
                "message": "Request was succesfully completed",
                "timestamp": "2025-01-11T21:56:00.000Z",
                "data": {
                    "id": "insight_id",
                    "account_id": "659d61857baef05dd147fd8f",
                    "status": "completed",
                    "created_at": "2025-01-11T21:56:00.000Z",
                    "updated_at": "2025-01-11T21:56:00.000Z"
                }
            }
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

        Example:
            >>> client.get_statement_insight_records("account_id")
            {
                "status": "successful",
                "message": "Request was succesfully completed",
                "timestamp": "2025-01-11T21:57:00.000Z",
                "data": [
                    {
                        "id": "insight_id",
                        "account_id": "659d61857baef05dd147fd8f",
                        "status": "completed",
                        "created_at": "2025-01-11T21:56:00.000Z",
                        "updated_at": "2025-01-11T21:56:00.000Z"
                    }
                ]
            }
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
