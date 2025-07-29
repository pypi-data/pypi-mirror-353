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
        """
        url = f"{self.BASE_URL}/v2/accounts"
        resp = self.session.get(url, params=params)
        if not resp.ok:
            raise MonoCustomerError(f"{resp.status_code}: {resp.text}")
        return resp.json()
