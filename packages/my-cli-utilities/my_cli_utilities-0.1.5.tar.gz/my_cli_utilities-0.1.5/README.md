# Account Pool CLI

A simple CLI tool to interact with the account pool service, allowing you to fetch account details.

## Installation

To install the Account Pool CLI, run the following command in your terminal:

```bash
pip install .
```

(If you publish it to PyPI, you would use `pip install account-pool-cli`)

## Usage

Once installed, you can use the `ap` command:

### Get account info by main number

```bash
ap info <main_number> [--env_name <environment_name>]
```
Example:
```bash
ap info 1234567890
ap info +1234567890 --env_name specific_env
```
`env_name` defaults to `webaqaxmn` if not provided.

### Get a random account

```bash
ap get_random_account <account_type> [--env_name <environment_name>]
```
Example:
```bash
ap get_random_account "QQ" 
ap get_random_account "YOUR_ACCOUNT_TYPE" --env_name specific_env
```

### Get account info by ID

```bash
ap get_account_by_id <account_id> [--env_name <environment_name>]
```
Example:
```bash
ap get_account_by_id "60c72b2f9b1d8f001f8e4d3a"
ap get_account_by_id "60c72b2f9b1d8f001f8e4d3b" --env_name specific_env
```

## Development

To set up for development:

1. Clone the repository.
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `source .venv/bin/activate` (on Linux/macOS) or `.venv\Scripts\activate` (on Windows)
4. Install dependencies: `pip install -r requirements-dev.txt` (You'll need to create this file if you have dev-specific dependencies like `pytest`)
5. Install the package in editable mode: `pip install -e .`