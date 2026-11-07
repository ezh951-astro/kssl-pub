import os
from pathlib import Path

import boto3
import duckdb
from dotenv import load_dotenv

from config import load_global_config

load_dotenv()

MARTS_DIRS = [
    Path("kessel_dbt/models/marts"),
    Path("kessel_dbt/models/gpr_marts")
]

def upload_to_aws(set_name):

    bucket = os.environ.get("S3_BUCKET")
    if not bucket or boto3.Session().get_credentials() is None:
        print("AWS not configured, skipping upload")
        return None

    s3 = boto3.client("s3")

    db_path = load_global_config(set_name).paths_dbt.duckdb
    mart_names = sorted({p.stem for d in MARTS_DIRS for p in d.rglob("*.sql")})

    failed = []
    with duckdb.connect(str(db_path), read_only=True) as con:

        tables = con.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
            AND list_contains(?, table_name)
            """,
            [mart_names]
        ).fetchall()

        for schema, table in tables:

            table_name = f"{table}.parquet"
            parquet = Path("temp") / table_name

            try:
                con.execute(
                    f"COPY (SELECT * FROM \"{schema}\".\"{table}\") "
                    f"TO '{parquet}' (FORMAT parquet, COMPRESSION zstd)"
                )
                s3.upload_file(str(parquet), bucket, f"{set_name}/{table_name}")
                print(f"Uploaded {set_name}/{table_name}")

            except Exception as e:
                failed.append(table_name)
                print(f"Failed {table_name}: {e}")

            finally:
                parquet.unlink(missing_ok=True)

    if failed:
        print(f"{len(failed)} of {len(tables)} tables failed: {', '.join(failed)}")