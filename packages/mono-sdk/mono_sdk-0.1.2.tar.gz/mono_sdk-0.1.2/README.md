# mono-connect

Python SDK for Mono Connect APIs.

## Features

- Retrieve account details, identity, balance, and transactions
- Unlink accounts
- Get account earnings and assets
- Initiate account linking and reauthorization
- Exchange tokens for account IDs
- Retrieve account statements and jobs
- Data enrichment: transaction categorisation, metadata, and statement insights
- Manage customers: create, retrieve, update, delete, list, fetch transactions, fetch linked accounts
- Directpay: one-time payments, verify, fetch payments, mandates, debit, balance, etc
- **Lookup: BVN, CAC, TIN, NIN, passport, driver's license, account number, address, credit history, mashup, bank listing**

## Installation

```bash
pip install mono-sdk
```

## Usage

### Mono Connect

```python
from mono_connect import MonoConnectClient

client = MonoConnectClient("your-mono-sec-key")

# Get account details
account = client.get_account_details("account_id")
print(account)

# Get account identity
identity = client.get_account_identity("account_id")
print(identity)

# Get account balance
balance = client.get_account_balance("account_id")
print(balance)

# Get transactions
transactions = client.get_transactions("account_id", narration="Uber", type="debit", limit=10)
print(transactions)

# Unlink account
client.unlink_account("account_id")

# Initiate account linking
linking = client.initiate_account_linking({
    "customer": {"name": "Samuel Nomo", "email": "Samuel@nomo.co"},
    "meta": {"ref": "1804008877TEST"},
    "scope": "auth",
    "redirect_url": "https://mono.co"
})
print(linking)
```

### Mono Customer

```python
from mono_customer import MonoCustomerClient

customer_client = MonoCustomerClient("your-mono-sec-key")

# Create a customer
customer = customer_client.create_customer({
    "email": "johndoe@mono.co",
    "firstName": "John",
    "lastName": "Doe",
    "address": "34 babasuwe street, namaco, ijebu ode, ogun state",
    "phone": "08003877665",
    "identity": {"type": "bvn", "number": "01234567891"}
})
print(customer)

# Retrieve a customer
customer = customer_client.retrieve_customer("customer_id")
print(customer)

# List customers
customers = customer_client.list_customers()
print(customers)

# Update a customer
updated = customer_client.update_customer("customer_id", {"address": "new address"})
print(updated)

# Delete a customer
deleted = customer_client.delete_customer("customer_id")
print(deleted)

# Get customer transactions
txns = customer_client.get_customer_transactions("customer_id", period="last12months", page=1)
print(txns)

# Fetch all linked accounts
accounts = customer_client.fetch_linked_accounts(page=1)
print(accounts)
```

### Mono Directpay

```python
from mono_directpay import MonoDirectpayClient

directpay = MonoDirectpayClient("your-mono-sec-key")

# Initiate a one-time payment
payment = directpay.initiate_payment({
    "amount": 20000,
    "type": "onetime-debit",
    "description": "testing",
    "reference": "testing9011",
    "redirect_url": "https://mono.co",
    "method": "account",
    "customer": {
        "email": "samuel5@nomo.co",
        "phone": "08111223344",
        "address": "home address",
        "identity": {"type": "bvn", "number": "43000382244"},
        "name": "Samuel"
    }
})
print(payment)

# Verify a transaction
result = directpay.verify_transaction("reference_id")
print(result)

# Fetch all payments
payments = directpay.fetch_all_payments(page=1, status="successful")
print(payments)

# Create a mandate
mandate = directpay.create_mandate({
    "debit_type": "variable",
    "customer": "customer_id",
    "mandate_type": "emandate",
    "amount": "10000",
    "reference": "string",
    "account_number": "string",
    "bank_code": "string",
    "description": "string",
    "start_date": "01-01-2024",
    "end_date": "01-01-2025"
})
print(mandate)

# Fetch all mandates
mandates = directpay.fetch_all_mandates(limit=5, page=1)
print(mandates)
```

### Mono Lookup

```python
from mono_lookup import MonoLookupClient

lookup = MonoLookupClient("your-mono-sec-key")

# Initiate BVN lookup
bvn = lookup.initiate_bvn_lookup({"bvn": "12345678901"})
print(bvn)

# Lookup CAC business
business = lookup.lookup_business("Mono")
print(business)

# Lookup TIN
tin = lookup.lookup_tin({"number": "1234567890", "channel": "tin"})
print(tin)

# Lookup NIN
nin = lookup.lookup_nin({"nin": "12345678901"})
print(nin)

# Lookup passport
passport = lookup.lookup_passport({"passport_number": "B50500882", "last_name": "Hassan", "date_of_birth": "1996-05-06"})
print(passport)

# Lookup driver's license
dl = lookup.lookup_driver_license({"license_number": "AAD23208212298", "date_of_birth": "2020-06-01", "first_name": "Samuel", "last_name": "Olamide"})
print(dl)

# Lookup account number
acct = lookup.lookup_account_number({"nip_code": "000015", "account_number": "0123456789"})
print(acct)

# Verify address
address = lookup.verify_address({"meter_number": "string", "address": "string"})
print(address)

# Credit history
credit = lookup.credit_history("xds", {"bvn": "22*******44"})
print(credit)

# Mashup
mashup = lookup.mashup({"nin": "0000000000", "bvn": "0000000000", "dob": "1990-01-01"})
print(mashup)

# Bank listing
banks = lookup.bank_listing()
print(banks)
```

## Error Handling

All methods raise `MonoConnectError`, `MonoCustomerError`, `MonoDirectpayError`, or `MonoLookupError` on non-successful responses.

## License

MIT
