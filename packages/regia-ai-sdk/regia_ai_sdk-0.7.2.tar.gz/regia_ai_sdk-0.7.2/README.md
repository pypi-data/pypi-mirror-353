# Regia AI SDK

A lightweight Python SDK to interact with the Regia Vision Extractor API.  
Send PDF documents and automatically extract structured data using Pydantic schemas.

---

## 📦 Installation

Using **pip**:

```bash
pip install regia-ai-sdk
```

or **uv** use the command line:

```bash
uv add regia-ai-sdk
```

## 🚀 Quickstart

```python
from regia_ai_sdk.vision import VisionClient
from pydantic import BaseModel, Field
import os

class InvoiceModel(BaseModel):
  due_date: str = Field(..., description="The due date of the invoice")
  total_amount: float = Field(..., description="The total amount of the invoice")

token = os.getenv("API_TOKEN")

client = VisionClient(token=token)

result = client.extract("./data/sample.pdf", InvoiceModel)
print(result)
```

## 📂 Other Input Methods

### From bytes

```python
with open("./data/sample.pdf", "rb") as f:
  content_bytes = f.read()

result = client.extract(content_bytes, InvoiceModel, filename="sample_bytes.pdf")
print(result)
```

### From base64

```python
import base64

with open("./data/sample.pdf", "rb") as f:
  base64_string = base64.b64encode(f.read()).decode("utf-8")

result = client.extract(base64_string, InvoiceModel, filename="sample_base64.pdf")
print(result)
```

## 🧠 Features

- ✅ Simple interface for sending documents to the Regia Vision API
- ✅ Supports file path, bytes, and base64 inputs
- ✅ Use Pydantic models to define the expected data
- ✅ Automatically converts Pydantic to schema JSON

## 🔐 Authentication

You must provide an API token and base URL:

```bash
export API_TOKEN=your_api_token_here
```

---

Made with 💡 by [Regia.ai](https://regia.ai)
