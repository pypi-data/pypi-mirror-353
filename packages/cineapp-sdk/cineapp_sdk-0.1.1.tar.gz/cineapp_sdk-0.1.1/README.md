# 🎬 CineAPP SDK – `cineapp-sdk`

A lightweight and user-friendly Python SDK for interacting with the CineAPP REST API, built on top of the MovieLens dataset.  
Designed for **Data Analysts**, **Data Scientists**, and learners — with native support for **Pydantic models**, **Python dictionaries**, and **Pandas DataFrames**.

[![PyPI version](https://badge.fury.io/py/cineapp-sdk.svg)](https://badge.fury.io/py/cineapp-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 📦 Installation

```bash
pip install cineapp-sdk
```

---

## ⚙️ Configuration

```python
from cineapp_sdk import CineClient, CineConfig

# Connect to the CineAPP API (hosted version)
config = CineConfig(cine_base_url="https://cineapp-xl99.onrender.com")
client = CineClient(config=config)
```

---

## ✅ Quick Examples

### 1. Health check

```python
client.health_check()
```

### 2. Get a movie by ID

```python
movie = client.get_movie(15)
print("Movie with ID = 15 is :", movie.title)
```

### 3. List First 5 Movies as a DataFrame

```python
df = client.list_movies(limit=5, output_format="pandas")
print(df.head())
```

---

## 🔄 Output Modes
All listing methods (`list_movies`, `list_ratings`, etc.) support the following output formats:

- **pydantic** (default) → List of Pydantic model instances

- **dict** → Raw dictionaries

- **pandas** → DataFrame for data analysis

Exemple :

```python
client.list_movies(limit=50, output_format="dict")
client.list_ratings(limit=50, output_format="pandas")
```

---

## 🧪 Local API Testing

You can also connect to a local FastAPI instance if running CineAPP locally:

```python
config = CineConfig(cine_base_url="http://localhost:8000")
client = CineConfig(config=config)
```

---

## 📝 Licence

This project is licensed under the MIT License.

---

## 🔗 Useful Links

- 🔍API Render : [https://cineapp-xl99.onrender.com/docs](https://cineapp-xl99.onrender.com/docs)
- 📦PyPI Package : [https://pypi.org/project/cineapp-sdk](https://pypi.org/project/cineapp-sdk)