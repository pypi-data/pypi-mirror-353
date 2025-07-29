
## Project Overview

This repository is a simple showcase Python package demonstrating how to use [dlt](https://dlthub.com/) for data extraction and loading. The package is structured to extract data from sources and load it into parquet, DuckDB and etc, serving as a reference for integrating dlt in your own projects.

## Getting Started

### Clone and run 
import package from pypi or clone and run
```bash
git clone https://github.com/e-espootin/poc_dlthub
cd poc_dlthub
make run
```



The main dlt pipeline file is located at:

```
src/app/ingest/
```
- ignore : src\app\utils

Refer to this path when running or modifying the pipeline.

## Managing Secrets

Sensitive information such as API keys or credentials should be managed securely:

- **GitHub Actions:** Store secrets using [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets).
- **Databricks:** Use [Databricks Secret Scopes](https://docs.databricks.com/en/security/secrets/index.html) for secure storage.



### connect to duckdb
```bash
duckdb .../rest_api_github.duckdb
show all tables;
```
---

### create dlt from scratch
```bash
uv init
uv venv --python 3.12
uv pip install -U dlt
dlt --version
dlt init rest_api duckdb
```
