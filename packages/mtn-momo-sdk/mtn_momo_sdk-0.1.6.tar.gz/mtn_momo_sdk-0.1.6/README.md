
# momo-sdk

A lightweight Python SDK to interact with the MTN MoMo (Mobile Money) API. Supports sandbox and live environments for mobile money collections.

---

## 🔧 Features

- Get access tokens (sandbox or live)
- Check account holder status
- Request mobile money payments
- Track transaction status

---

## 📦 Installation

Install from [PyPI](https://pypi.org/project/momo-sdk/):

```bash
pip install mtn-momo-sdk
```

Or install from source:

```bash
git clone https://github.com/yourusername/mtn-momo.git
cd mtn-momo
pip install .
```

---

## 🛠️ Setup

To start using the SDK, instantiate the `Momo` class with your credentials:

```python
from momo_sdk import Momo
import uuid

momo = Momo(
    api_user="your_api_user",
    api_key="your_api_key",
    subscription_key="your_subscription_key",
    mode="development", # or "production"
    callback_url='your_callbackurl' # e.g https://example.com
)
```

---

## 🚀 Usage

### ✅ 1. Get API Context

```python
print(momo.get_env())         # sandbox or mtnuganda
print(momo.get_url())         # Base API URL
print(momo.get_callback())    # Callback URL
```

---

### 📞 2. Check Account Status

```python
status = momo.get_accountholder("256771234567")
print(status)
```

---

### 💰 3. Request Mobile Money Payment

```python
transaction_id = str(uuid.uuid4())

response = momo.deposit_money(
    msisdn="256771234567",  # Customer MSISDN
    amount="10000",         # Amount in UGX or EUR
    reference=transaction_id
)

print(response)
```

---

### 📦 4. Check Transaction Status

```python
result = momo.get_transaction(transaction_id)
print(result)
```

---

## 📁 Project Structure

```
momo_sdk/
├── momo.py           # SDK module
├── __init__.py
├── setup.py
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## 🧪 Testing the API

> Sandbox credentials are required from:  
> [https://momodeveloper.mtn.com/](https://momodeveloper.mtn.com/)

Make sure:
- Your callback URL is set in the MTN portal
- Your user is created and provisioned
- The subscription key is the primary or secondary key for collections product subscribed on the portal
- Subscription key is valid for `collection`

---

## 📫 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss your ideas.

---

## 📝 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Your Name**  
GitHub: [@brucekyl](https://github.com/brucekyl)  
Email: bbagarukayo5@gmail.com

---

## 🚨 Disclaimer

Use this SDK at your own risk. Ensure you follow MTN MoMo's terms, guidelines, and security protocols before deploying to production.
