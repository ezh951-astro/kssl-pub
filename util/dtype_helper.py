DTYPES = {
    "int":       {"numpy": "int64",   "pandas": "Int64",   "duckdb": "BIGINT"},
    "float":     {"numpy": "float64", "pandas": "Float64", "duckdb": "DOUBLE"},
    "int8":      {"numpy": "int8",    "pandas": "Int8",    "duckdb": "TINYINT"},
    "int16":     {"numpy": "int16",   "pandas": "Int16",   "duckdb": "SMALLINT"},
    "int32":     {"numpy": "int32",   "pandas": "Int32",   "duckdb": "INTEGER"},
    "int64":     {"numpy": "int64",   "pandas": "Int64",   "duckdb": "BIGINT"},
    "uint8":     {"numpy": "uint8",   "pandas": "UInt8",   "duckdb": "UTINYINT"},
    "uint16":    {"numpy": "uint16",  "pandas": "UInt16",  "duckdb": "USMALLINT"},
    "uint32":    {"numpy": "uint32",  "pandas": "UInt32",  "duckdb": "UINTEGER"},
    "uint64":    {"numpy": "uint64",  "pandas": "UInt64",  "duckdb": "UBIGINT"},
    "float32":   {"numpy": "float32", "pandas": "Float32", "duckdb": "FLOAT"},
    "float64":   {"numpy": "float64", "pandas": "Float64", "duckdb": "DOUBLE"},
    "bool":      {"numpy": "bool",    "pandas": "boolean", "duckdb": "BOOLEAN"},
    "text":      {"numpy": "object",  "pandas": "string",  "duckdb": "VARCHAR"},
    "timestamp": {"numpy": "datetime64[ns]", "pandas": "datetime64[ns]", "duckdb": "TIMESTAMP"},
    "date":      {"numpy": "datetime64[D]",  "pandas": "date32[pyarrow]", "duckdb": "DATE"},
    "duration":  {"numpy": "timedelta64[ns]", "pandas": "timedelta64[ns]", "duckdb": "INTERVAL"},
    "category":  {"numpy": None,      "pandas": "category", "duckdb": "ENUM"},
    "decimal":   {"numpy": None,      "pandas": "decimal128[pyarrow]", "duckdb": "DECIMAL(18,3)"},
    "hugeint":   {"numpy": None,      "pandas": None,       "duckdb": "HUGEINT"},
}

NUMPY_TO_PANDAS = {v["numpy"]: v["pandas"] for v in DTYPES.values() if v["numpy"] and v["pandas"]}
NUMPY_TO_DUCKDB = {v["numpy"]: v["duckdb"] for v in DTYPES.values() if v["numpy"]}
PANDAS_TO_DUCKDB = {v["pandas"]: v["duckdb"] for v in DTYPES.values() if v["pandas"]}

###

def get_dtype(dtype: str, dformat: str):

    if dformat not in ["numpy", "pandas", "duckdb"]:
        raise ValueError("Can only get dtypes in numpy, pandas, duckdb")

    if dtype not in DTYPES:
        raise ValueError(f"Invalid dtype '{dtype}', must be one of {list(DTYPES)}")

    if DTYPES[dtype][dformat] is None:
        raise ValueError(f"dtype '{dtype}' has no {dformat} equivalent")

    return DTYPES[dtype][dformat]
    