# 🎉 fetti

**fetti** is a lightweight CLI tool to inject environment variables from a TOML config file and run any command with them. Think of it like `dotenv`, but for TOML — with live command execution and optional scoping by namespace.
- - -
## 🚀 Features
- ✅ Parse environment variables from a `.toml` config file
- ✅ Interpolate values like `${OTHER_VAR}` from within the same scope
- ✅ Inject variables into any command (`--`)
- ✅ Support scoped namespaces (e.g., `[database]`)
- ✅ Minimal, fast, zero-runtime dependencies (except `click`)

- - -

## 📦 Installation

```bash
pip install fetti
```


## 🧪 Example

Given a config file `config.toml`:

```toml
[database]
host = "localhost"
port = 5432
user = "admin"
url = "postgres://${DATABASE_USER}@${DATABASE_HOST}:${DATABASE_PORT}/mydb"
```

You can run a script with these injected:

```bash
fetti config.toml -n database -- python my_script.py
```

In `my_script.py`, you’ll have access to:

```python
import os

print(os.environ["DATABASE_URL"])
```

## ⚙️ CLI Usage

```bash
fetti [OPTIONS] FILE -- COMMAND [ARGS]...
```

### Arguments

Name

Description

`FILE`

Path to your TOML config file

`--`

Everything after `--` is the command to run

### Options

Flag

Description

`-n, --namespace NAME`

Use a specific top-level section from TOML

* * *

## 🛠 Advanced Example

```bash
fetti settings.toml -- env | grep API_
```

With a config like:

```toml
[api]
key = "1234"
url = "https://api.example.com"
```

Would print:

```bash
API_KEY=1234
API_URL=https://api.example.com
```

### Flatten Nested Dicts
```toml
[service]
name = "api"

[service.env]
debug = true

[service.env.db]
host = "localhost"
port = 5432
url = "postgres://${SERVICE_ENV_DB_HOST}:${SERVICE_ENV_DB_PORT}"
```


```bash
fetti config.toml -n service -- printenv | grep SERVICE_
```
Output:
```bash
SERVICE_NAME=api
SERVICE_ENV_DEBUG=true
SERVICE_ENV_DB_HOST=localhost
SERVICE_ENV_DB_PORT=5432
SERVICE_ENV_DB_URL=postgres://localhost:5432
```

## 📄 License

MIT License

