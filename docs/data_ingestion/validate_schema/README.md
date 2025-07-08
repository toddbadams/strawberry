**Problem Statement**
You need a small Python utility that, for every Parquet file you land, compares its actual column set and types against your “golden” schema—and if anything’s missing, extra, or changed, fires off a Slack alert so you can fix it before downstream jobs break.

---

## Solution Overview

1. **Define the Expected Schema**

   * Store your master schema in code (as a PyArrow `Schema` object) or in a simple JSON/YAML file that maps column names → data types.

2. **Read & Extract the Parquet Schema**

   * Use **PyArrow** to open each Parquet file and pull its arrow schema:

     ```python
     from pyarrow.parquet import ParquetFile

     def load_parquet_schema(path: str) -> pa.Schema:
         pf = ParquetFile(path)
         return pf.schema.to_arrow_schema()
     ```

3. **Compare Schemas**

   * Iterate your expected fields and types, and check against the actual schema’s fields.
   * Catch three classes of anomalies:

     1. **Missing columns**
     2. **Extra columns**
     3. **Type mismatches**
   * Collect all discrepancies into a list of human-readable error strings.

4. **Notify via Slack**

   * Use a Slack **Incoming Webhook** (URL stored in `SLACK_WEBHOOK_URL` env var)
   * Post a JSON payload summarizing the anomalies:

     ```python
     import os, requests

     SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")

     def alert_slack(message: str):
         payload = {"text": message}
         resp = requests.post(SLACK_WEBHOOK, json=payload)
         resp.raise_for_status()
     ```

5. **Glue It Together in a Job**

   * Scan your Parquet folder (or be given a list), run the check on each file, and if any errors are found call `alert_slack()` once per file (or batch them).
   * Exit with a non-zero code if you want your orchestration tool (Prefect, cron-wrapper) to mark the run as failed.

---

## Example Code Sketch

```python
import os
import json
import pa​yarrow as pa
import requests
from pyarrow.parquet import ParquetFile

# 1. Load “golden” schema from JSON
def load_expected_schema(json_path="expected_schema.json") -> pa.Schema:
    with open(json_path) as f:
        schema_dict = json.load(f)
    fields = [pa.field(name, getattr(pa, dtype)()) 
              for name, dtype in schema_dict.items()]
    return pa.schema(fields)

# 2. Read actual schema from Parquet
def load_parquet_schema(path: str) -> pa.Schema:
    pf = ParquetFile(path)
    return pf.schema.to_arrow_schema()

# 3. Compare schemas and collect anomalies
def compare_schemas(expected: pa.Schema, actual: pa.Schema) -> list[str]:
    errors = []
    exp_fields = {f.name: f.type for f in expected}
    act_fields = {f.name: f.type for f in actual}
    
    # Missing
    for name in exp_fields:
        if name not in act_fields:
            errors.append(f"❌ Missing column: {name}")
    # Extra
    for name in act_fields:
        if name not in exp_fields:
            errors.append(f"⚠️ Unexpected column: {name}")
    # Type mismatch
    for name in exp_fields.keys() & act_fields.keys():
        if exp_fields[name] != act_fields[name]:
            errors.append(f"🚨 Type mismatch for '{name}': expected {exp_fields[name]}, got {act_fields[name]}")
    return errors

# 4. Slack notifier
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")
def alert_slack(file_path: str, errors: list[str]):
    text = f"*Schema issues detected* for `{file_path}`:\n" + "\n".join(errors)
    resp = requests.post(SLACK_WEBHOOK, json={"text": text})
    resp.raise_for_status()

# 5. Main job
def validate_parquet_files(file_paths: list[str]):
    expected = load_expected_schema()
    for path in file_paths:
        actual = load_parquet_schema(path)
        errors = compare_schemas(expected, actual)
        if errors:
            alert_slack(path, errors)

if __name__ == "__main__":
    # Example: pass in a list of files or glob your data lake
    files = ["data/2025_Q1/ABC.parquet", "data/2025_Q1/DEF.parquet"]
    validate_parquet_files(files)
```

---

### Next Steps

1. **Write** an `expected_schema.json` that lists each column name and its Arrow type (`"string"`, `"int64"`, etc.).
2. **Install** PyArrow and `requests` in your ingestion Docker image.
3. **Test** locally with a “good” file and a file you tweak to break the schema.
4. **Plug** the script into your Prefect/cron flow and ensure Slack alerts look clean.
