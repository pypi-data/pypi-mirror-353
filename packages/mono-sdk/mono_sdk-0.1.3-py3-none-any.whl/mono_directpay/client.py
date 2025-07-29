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

        Example:
            >>> client.initiate_payment({
            ...     "amount": 20000,
            ...     "type": "onetime-debit",
            ...     "description": "testing",
            ...     "reference": "testing9011",
            ...     "redirect_url": "https://mono.co",
            ...     "method": "account",
            ...     "customer": {
            ...         "email": "samuel5@nomo.co",
            ...         "phone": "08111223344",
            ...         "address": "home address",
            ...         "identity": {"type": "bvn", "number": "43000382244"},
            ...         "name": "Samuel"
            ...     }
            ... })
            {
                "status": "successful",
                "message": "Payment Initiated Successfully",
                "data": {
                    "id": "ODPDVM49HEFY",
                    "mono_url": "https://checkout.mono.co/ODPDVM49HEFY",
                    "type": "onetime-debit",
                    "method": "account",
                    "amount": 20000,
                    "description": "tetsing",
                    "reference": "l09861141090110039819098",
                    "customer": "65de6b3bfe29300fb5606140",
                    "redirect_url": "https://mono.co",
                    "created_at": "2024-03-15T06:54:12.127Z",
                    "updated_at": "2024-03-15T06:54:12.127Z",
                    "meta": {}
                }
            }
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

        Example:
            >>> client.verify_transaction("demo_ref_mxy0mbi123")
            {
                "status": "successful",
                "message": "Payment retrieved successfully",
                "timestamp": "2024-04-27T21:57:26.609Z",
                "data": {
                    "id": "txdsgcamwweg62h0msjfx512345",
                    "channel": "account",
                    "fee": 100,
                    "type": "onetime-debit",
                    "status": "successful",
                    "amount": 20000,
                    "currency": "NGN",
                    "description": "DirectPay Demo",
                    "reference": "demo_ref_mxy0mbi123",
                    "live_mode": true,
                    "account": {
                        "id": "65c525b7a6ce43abef77c123",
                        "name": "SAMUEL OLAMIDE",
                        "account_number": "90123456789",
                        "currency": "NGN",
                        "balance": 478915,
                        "type": "WALLET ACCOUNT",
                        "bvn": "98765432123",
                        "live_mode": true,
                        "institution": {
                            "name": "Opay",
                            "type": "PERSONAL_BANKING",
                            "timeout": 50000,
                            "available": true,
                            "scope": [
                                "payments",
                                "financial_data"
                            ],
                            "bank_code": "100004"
                        },
                        "scope": [
                            "payments"
                        ]
                    },
                    "customer": "6615f0a97f633aefa2e6c123",
                    "refunded": true,
                    "device_fingerprint": "12345678-123b-45db-b678-91a0a2ed1234",
                    "ip_address": "1.1.1.1",
                    "created_at": "2024-04-10T01:51:54.189Z",
                    "updated_at": "2024-04-12T05:24:51.396Z",
                    "meta": {
                        "locked": null
                    }
                }
            }
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

        Example:
            >>> client.fetch_all_payments(page=1, status="successful")
            {
                "status": "successful",
                "message": "Data retrieved successfully",
                "timestamp": "2024-04-27T22:33:51.602Z",
                "data": {
                    "payments": [
                        {
                            "id": "63f0000025a00000749a7768",
                            "type": "onetime-debit",
                            "status": "pending",
                            "amount": 325000,
                            "description": "Books and Sports Limited",
                            "currency": "NGN",
                            "account": {
                                "id": "63f4e6621749a7762",
                                "institution": {
                                    "id": "5f2d08888287702",
                                    "name": "GTBank",
                                    "type": "PERSONAL_BANKING"
                                },
                                "name": "SAMUEL OLAMIDE",
                                "account_number": "02540000289",
                                "currency": "NGN",
                                "created_at": "2023-02-21T15:42:26.446Z",
                                "updated_at": "2023-02-21T15:42:26.483Z"
                            },
                            "customer": null,
                            "reference": "VQCM993958971200",
                            "created_at": "2023-02-21T15:42:26.965Z",
                            "updated_at": "2023-02-21T15:42:26.965Z"
                        }
                    ]
                },
                "meta": {
                    "paging": {
                        "total": 249440,
                        "pages": 49888,
                        "previous": null,
                        "next": "https://api.withmono.com/v2/payments/transactions?page=2"
                    }
                }
            }
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

        Example:
            >>> client.get_banks()
            {
                "status": "successful",
                "message": "Banks retrieved successfully",
                "data": [
                    {
                        "id": "bank_1",
                        "name": "Bank A",
                        "code": "123",
                        "type": "commercial",
                        "country": "NG",
                        "currency": "NGN",
                        "logo": "https://example.com/logo_a.png"
                    },
                    {
                        "id": "bank_2",
                        "name": "Bank B",
                        "code": "456",
                        "type": "commercial",
                        "country": "NG",
                        "currency": "NGN",
                        "logo": "https://example.com/logo_b.png"
                    }
                ]
            }
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

        Example:
            >>> client.create_mandate({
            ...     "customer": "cus_123456789",
            ...     "amount": 10000,
            ...     "currency": "NGN",
            ...     "interval": "monthly",
            ...     "start_date": "2024-01-01",
            ...     "end_date": "2024-12-31",
            ...     "description": "Monthly subscription",
            ...     "reference": "mandate_ref_001",
            ...     "metadata": {"key1": "value1", "key2": "value2"}
            ... })
            {
                "status": "successful",
                "message": "Mandate created successfully",
                "data": {
                    "id": "man_123456789",
                    "customer": "cus_123456789",
                    "amount": 10000,
                    "currency": "NGN",
                    "interval": "monthly",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "description": "Monthly subscription",
                    "reference": "mandate_ref_001",
                    "status": "active",
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "updated_at": "2024-01-01T00:00:00.000Z",
                    "metadata": {"key1": "value1", "key2": "value2"}
                }
            }
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

        Example:
            >>> client.initiate_mandate({
            ...     "amount": 10000,
            ...     "currency": "NGN",
            ...     "interval": "monthly",
            ...     "start_date": "2024-01-01",
            ...     "end_date": "2024-12-31",
            ...     "description": "Monthly subscription",
            ...     "reference": "mandate_ref_001",
            ...     "customer": {
            ...         "email": "samuel5@nomo.co",
            ...         "phone": "08111223344",
            ...         "address": "home address",
            ...         "identity": {"type": "bvn", "number": "43000382244"},
            ...         "name": "Samuel"
            ...     }
            ... })
            {
                "status": "successful",
                "message": "Mandate initiated successfully",
                "data": {
                    "id": "man_987654321",
                    "customer": "cus_123456789",
                    "amount": 10000,
                    "currency": "NGN",
                    "interval": "monthly",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "description": "Monthly subscription",
                    "reference": "mandate_ref_001",
                    "status": "pending",
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "updated_at": "2024-01-01T00:00:00.000Z",
                    "metadata": {}
                }
            }
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

        Example:
            >>> client.mandate_status("man_123456789")
            {
                "status": "successful",
                "message": "Mandate status retrieved successfully",
                "data": {
                    "id": "man_123456789",
                    "status": "active",
                    "next_payment_date": "2024-05-01",
                    "last_payment_date": "2024-04-01",
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "updated_at": "2024-04-01T00:00:00.000Z"
                }
            }
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

        Example:
            >>> client.retrieve_mandate("man_123456789")
            {
                "status": "successful",
                "message": "Mandate retrieved successfully",
                "data": {
                    "id": "man_123456789",
                    "customer": "cus_123456789",
                    "amount": 10000,
                    "currency": "NGN",
                    "interval": "monthly",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "description": "Monthly subscription",
                    "reference": "mandate_ref_001",
                    "status": "active",
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "updated_at": "2024-01-01T00:00:00.000Z",
                    "metadata": {"key1": "value1", "key2": "value2"}
                }
            }
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

        Example:
            >>> client.fetch_all_mandates(page=1, status="active")
            {
                "status": "successful",
                "message": "Data retrieved successfully",
                "timestamp": "2024-04-27T22:33:51.602Z",
                "data": {
                    "mandates": [
                        {
                            "id": "man_123456789",
                            "customer": "cus_123456789",
                            "amount": 10000,
                            "currency": "NGN",
                            "interval": "monthly",
                            "start_date": "2024-01-01",
                            "end_date": "2024-12-31",
                            "description": "Monthly subscription",
                            "reference": "mandate_ref_001",
                            "status": "active",
                            "created_at": "2024-01-01T00:00:00.000Z",
                            "updated_at": "2024-01-01T00:00:00.000Z",
                            "metadata": {"key1": "value1", "key2": "value2"}
                        }
                    ]
                },
                "meta": {
                    "paging": {
                        "total": 100,
                        "pages": 10,
                        "previous": null,
                        "next": "https://api.withmono.com/v3/payments/mandates?page=2"
                    }
                }
            }
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

        Example:
            >>> client.cancel_mandate("man_123456789")
            {
                "status": "successful",
                "message": "Mandate cancelled successfully",
                "data": {
                    "id": "man_123456789",
                    "status": "cancelled",
                    "cancellation_date": "2024-04-01",
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "updated_at": "2024-04-01T00:00:00.000Z"
                }
            }
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

        Example:
            >>> client.pause_mandate("man_123456789")
            {
                "status": "successful",
                "message": "Mandate paused successfully",
                "data": {
                    "id": "man_123456789",
                    "status": "paused",
                    "pause_date": "2024-04-01",
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "updated_at": "2024-04-01T00:00:00.000Z"
                }
            }
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

        Example:
            >>> client.reinstate_mandate("man_123456789")
            {
                "status": "successful",
                "message": "Mandate reinstated successfully",
                "data": {
                    "id": "man_123456789",
                    "status": "active",
                    "reinstate_date": "2024-04-01",
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "updated_at": "2024-04-01T00:00:00.000Z"
                }
            }
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

        Example:
            >>> client.verify_otp_mandate({
            ...     "mandate_id": "man_123456789",
            ...     "otp": "123456"
            ... })
            {
                "status": "successful",
                "message": "OTP verified successfully",
                "data": {
                    "id": "man_123456789",
                    "status": "active",
                    "otp_verified_at": "2024-01-01T00:00:00.000Z",
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "updated_at": "2024-01-01T00:00:00.000Z"
                }
            }
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

        Example:
            >>> client.balance_inquiry("man_123456789")
            {
                "status": "successful",
                "message": "Balance retrieved successfully",
                "data": {
                    "id": "man_123456789",
                    "balance": 50000,
                    "currency": "NGN",
                    "available_balance": 30000,
                    "held_balance": 20000,
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "updated_at": "2024-01-01T00:00:00.000Z"
                }
            }
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

        Example:
            >>> client.debit_account("man_123456789", {
            ...     "amount": 5000,
            ...     "currency": "NGN",
            ...     "description": "Payment for services",
            ...     "reference": "debit_ref_001"
            ... })
            {
                "status": "successful",
                "message": "Account debited successfully",
                "data": {
                    "id": "debit_123456789",
                    "mandate_id": "man_123456789",
                    "amount": 5000,
                    "currency": "NGN",
                    "description": "Payment for services",
                    "reference": "debit_ref_001",
                    "status": "successful",
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "updated_at": "2024-01-01T00:00:00.000Z"
                }
            }
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

        Example:
            >>> client.debit_account_beneficiary("man_123456789", {
            ...     "amount": 5000,
            ...     "currency": "NGN",
            ...     "description": "Payment to beneficiary",
            ...     "reference": "beneficiary_debit_ref_001"
            ... })
            {
                "status": "successful",
                "message": "Beneficiary account debited successfully",
                "data": {
                    "id": "beneficiary_debit_123456789",
                    "mandate_id": "man_123456789",
                    "amount": 5000,
                    "currency": "NGN",
                    "description": "Payment to beneficiary",
                    "reference": "beneficiary_debit_ref_001",
                    "status": "successful",
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "updated_at": "2024-01-01T00:00:00.000Z"
                }
            }
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

        Example:
            >>> client.retrieve_debit("man_123456789", "debit_123456789")
            {
                "status": "successful",
                "message": "Debit transaction retrieved successfully",
                "data": {
                    "id": "debit_123456789",
                    "mandate_id": "man_123456789",
                    "amount": 5000,
                    "currency": "NGN",
                    "description": "Payment for services",
                    "reference": "debit_ref_001",
                    "status": "successful",
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "updated_at": "2024-01-01T00:00:00.000Z"
                }
            }
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

        Example:
            >>> client.retrieve_all_debits("man_123456789", page=1)
            {
                "status": "successful",
                "message": "Data retrieved successfully",
                "timestamp": "2024-04-27T22:33:51.602Z",
                "data": {
                    "debits": [
                        {
                            "id": "debit_123456789",
                            "mandate_id": "man_123456789",
                            "amount": 5000,
                            "currency": "NGN",
                            "description": "Payment for services",
                            "reference": "debit_ref_001",
                            "status": "successful",
                            "created_at": "2024-01-01T00:00:00.000Z",
                            "updated_at": "2024-01-01T00:00:00.000Z"
                        }
                    ]
                },
                "meta": {
                    "paging": {
                        "total": 10,
                        "pages": 1,
                        "previous": null,
                        "next": null
                    }
                }
            }
        """
        url = f"{self.BASE_URL}/v3/payments/mandates/{mandate_id}/debits"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoDirectpayError(f"{resp.status_code}: {resp.text}")
        return resp.json()
