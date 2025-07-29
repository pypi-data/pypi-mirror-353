"""
mono_customer.client
--------------------
Python SDK client for Mono Customer APIs.
Provides methods for managing customers and retrieving customer-related data.
"""

import requests


class MonoCustomerError(Exception):
    """Custom exception for Mono Customer SDK errors."""

    pass


class MonoCustomerClient:
    """
    Client for interacting with the Mono Customer API.

    Args:
        sec_key (str): Your Mono secret key.
    """

    BASE_URL = "https://api.withmono.com"

    def __init__(self, sec_key: str):
        """
        Initialize the MonoCustomerClient.

        Args:
            sec_key (str): Your Mono secret key.
        """
        self.sec_key = sec_key
        self.session = requests.Session()
        self.session.headers.update({"mono-sec-key": self.sec_key})

    def create_customer(self, data):
        """
        Create a new customer (individual or business).

        Args:
            data (dict): Customer creation payload.

        Returns:
            dict: Customer creation response.

        Example:
            >>> client.create_customer({
            ...     "email": "johndoe@mono.co",
            ...     "firstName": "John",
            ...     "lastName": "Doe",
            ...     "address": "34 babasuwe street, namaco, ijebu ode, ogun state",
            ...     "phone": "08003877665",
            ...     "identity": {"type": "bvn", "number": "01234567891"}
            ... })
            {
                "status": "successful",
                "message": "Customer created successfully",
                "data": {
                    "id": "cus_1234567890abcdef",
                    "email": "johndoe@mono.co",
                    "firstName": "John",
                    "lastName": "Doe",
                    "address": "34 babasuwe street, namaco, ijebu ode, ogun state",
                    "phone": "08003877665",
                    "identity": {"type": "bvn", "number": "01234567891"}
                }
            }

        Reference:
            Mono Customer Postman Collection - Create Customer
        """
        url = f"{self.BASE_URL}/v2/customers"
        resp = self.session.post(url, json=data)
        if resp.status_code not in (200, 201):
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def retrieve_customer(self, customer_id):
        """
        Retrieve information about a single customer.

        Args:
            customer_id (str): The customer ID.

        Returns:
            dict: Customer data.

        Example:
            >>> client.retrieve_customer("cus_1234567890abcdef")
            {
                "status": "successful",
                "message": "Customer retrieved successfully",
                "data": {
                    "id": "cus_1234567890abcdef",
                    "email": "johndoe@mono.co",
                    "firstName": "John",
                    "lastName": "Doe",
                    "address": "34 babasuwe street, namaco, ijebu ode, ogun state",
                    "phone": "08003877665",
                    "identity": {"type": "bvn", "number": "01234567891"}
                }
            }

        Reference:
            Mono Customer Postman Collection - Retrieve Customer
        """
        url = f"{self.BASE_URL}/v2/customers/{customer_id}"
        resp = self.session.get(url)
        if not resp.ok:
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def list_customers(self, **params):
        """
        Retrieve information about all customers.

        Args:
            **params: Optional query parameters.

        Returns:
            dict: List of customers.

        Example:
            >>> client.list_customers(page=1, limit=10)
            {
                "status": "successful",
                "message": "Customers retrieved successfully",
                "data": [
                    {
                        "id": "cus_1234567890abcdef",
                        "email": "johndoe@mono.co",
                        "firstName": "John",
                        "lastName": "Doe"
                    },
                    {
                        "id": "cus_abcdef1234567890",
                        "email": "janedoe@mono.co",
                        "firstName": "Jane",
                        "lastName": "Doe"
                    }
                ],
                "meta": {
                    "page": 1,
                    "limit": 10,
                    "total": 2
                }
            }

        Reference:
            Mono Customer Postman Collection - List Customers
        """
        url = f"{self.BASE_URL}/v2/customers"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def update_customer(self, customer_id, data):
        """
        Update information about a single customer.

        Args:
            customer_id (str): The customer ID.
            data (dict): Update payload.

        Returns:
            dict: Update response.

        Example:
            >>> client.update_customer("cus_1234567890abcdef", {"address": "new address"})
            {
                "status": "successful",
                "message": "Customer updated successfully",
                "data": {
                    "id": "cus_1234567890abcdef",
                    "address": "new address"
                }
            }

        Reference:
            Mono Customer Postman Collection - Update Customer
        """
        url = f"{self.BASE_URL}/v2/customers/{customer_id}"
        resp = self.session.patch(url, json=data)
        if not resp.ok:
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def delete_customer(self, customer_id):
        """
        Delete a customer.

        Args:
            customer_id (str): The customer ID.

        Returns:
            dict: Delete response.

        Example:
            >>> client.delete_customer("cus_1234567890abcdef")
            {
                "status": "successful",
                "message": "Customer deleted successfully",
                "data": null
            }

        Reference:
            Mono Customer Postman Collection - Delete Customer
        """
        url = f"{self.BASE_URL}/v2/customers/{customer_id}"
        resp = self.session.delete(url)
        if not resp.ok:
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def get_customer_transactions(self, customer_id, **params):
        """
        Retrieve all transactions performed by a customer.

        Args:
            customer_id (str): The customer ID.
            **params: Optional query parameters.

        Returns:
            dict: Transactions data.

        Example:
            >>> client.get_customer_transactions("cus_1234567890abcdef", period="last12months", page=1)
            {
                "status": "successful",
                "message": "Transactions retrieved successfully",
                "data": [
                    {
                        "id": "txn_1",
                        "amount": 10000,
                        "type": "debit",
                        "narration": "Payment for services"
                    }
                ],
                "meta": {
                    "page": 1,
                    "limit": 10,
                    "total": 1
                }
            }

        Reference:
            Mono Customer Postman Collection - Get Customer Transactions
        """
        url = f"{self.BASE_URL}/customers/{customer_id}/transactions"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()

    def fetch_linked_accounts(self, **params):
        """
        Retrieve all accounts linked to a business.

        Args:
            **params: Optional query parameters.

        Returns:
            dict: Linked accounts data.

        Example:
            >>> client.fetch_linked_accounts(page=1)
            {
                "status": "successful",
                "message": "Linked accounts retrieved successfully",
                "data": [
                    {
                        "id": "acc_1234567890abcdef",
                        "account_number": "0123456789",
                        "bank": "GTBank"
                    }
                ],
                "meta": {
                    "page": 1,
                    "limit": 10,
                    "total": 1
                }
            }

        Reference:
            Mono Customer Postman Collection - Fetch Linked Accounts
        """
        url = f"{self.BASE_URL}/v2/accounts"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()
