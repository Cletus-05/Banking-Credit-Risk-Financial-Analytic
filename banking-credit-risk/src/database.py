"""
database.py
===========
Banking Credit Risk & Financial Analytics — Phase 4 Database Module

Purpose:
    Manages database connectivity, schema creation, data ingestion,
    and analytical query execution for the Credit Risk analytics pipeline.

Target Database:
    - MySQL 8.0+ (Production Analytical Store)
    - Validated on: MySQL Server 8.0.43

Configuration:
    Connection parameters are read securely from the project's .env file
    (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME).
    NEVER hardcode passwords or sensitive credentials in source code.

Author:  Banking Credit Risk Portfolio Project
Dataset: data/processed/credit_risk_clean.csv (30,000 records, 25 columns)
"""

import os
import sys
import re
import pandas as pd
import pymysql
from sqlalchemy import (
    create_engine, text, Table, Column, Integer, MetaData, Index
)
from sqlalchemy.engine import Engine, URL
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_CSV = os.path.join(BASE_DIR, "data", "processed", "credit_risk_clean.csv")
SQL_QUERIES_FILE = os.path.join(BASE_DIR, "sql", "analytics_queries.sql")


def get_mysql_engine() -> Engine:
    """
    Construct and return a SQLAlchemy Engine for the target MySQL 8.0+ database
    using URL.create to safely handle passwords with special characters.
    """
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "credit_risk_db")

    # Ensure database exists before creating connection pool
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password)
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
        conn.close()
    except Exception as e:
        print(f"[get_mysql_engine] Notice on pre-connection: {e}")

    url_object = URL.create(
        drivername="mysql+pymysql",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database
    )

    engine = create_engine(url_object, echo=False)
    return engine


def verify_mysql_connection(engine: Engine) -> dict:
    """
    Verify live MySQL server connectivity, returning server version and details.
    """
    with engine.connect() as conn:
        res = conn.execute(text("SELECT VERSION(), DATABASE(), USER()")).fetchone()
        info = {
            "version": res[0],
            "database": res[1],
            "user": res[2]
        }
    print(f"[verify_mysql_connection] Connected to MySQL Server version: {info['version']}")
    print(f"[verify_mysql_connection] Active Database: `{info['database']}` | User: {info['user']}")
    return info


def create_schema(engine: Engine) -> None:
    """
    Create the analytical table `credit_card_clients` schema with primary key,
    column types, and performance indexes in MySQL.
    """
    metadata = MetaData()

    credit_card_clients = Table(
        "credit_card_clients",
        metadata,
        Column("ID", Integer, primary_key=True, comment="Customer Identifier (1-30000)"),
        Column("LIMIT_BAL", Integer, nullable=False, comment="Credit Limit (NT$)"),
        Column("SEX", Integer, nullable=False, comment="Gender: 1=Male, 2=Female"),
        Column("EDUCATION", Integer, nullable=False, comment="Education: 1=Grad, 2=Univ, 3=HS, 4=Others"),
        Column("MARRIAGE", Integer, nullable=False, comment="Marital Status: 1=Married, 2=Single, 3=Others"),
        Column("AGE", Integer, nullable=False, comment="Age in years"),
        Column("PAY_0", Integer, nullable=False, comment="Repayment status Sep 2005 (-2 to 8)"),
        Column("PAY_2", Integer, nullable=False, comment="Repayment status Aug 2005 (-2 to 8)"),
        Column("PAY_3", Integer, nullable=False, comment="Repayment status Jul 2005 (-2 to 8)"),
        Column("PAY_4", Integer, nullable=False, comment="Repayment status Jun 2005 (-2 to 8)"),
        Column("PAY_5", Integer, nullable=False, comment="Repayment status May 2005 (-2 to 8)"),
        Column("PAY_6", Integer, nullable=False, comment="Repayment status Apr 2005 (-2 to 8)"),
        Column("BILL_AMT1", Integer, nullable=False, comment="Bill statement amount Sep 2005 (NT$)"),
        Column("BILL_AMT2", Integer, nullable=False, comment="Bill statement amount Aug 2005 (NT$)"),
        Column("BILL_AMT3", Integer, nullable=False, comment="Bill statement amount Jul 2005 (NT$)"),
        Column("BILL_AMT4", Integer, nullable=False, comment="Bill statement amount Jun 2005 (NT$)"),
        Column("BILL_AMT5", Integer, nullable=False, comment="Bill statement amount May 2005 (NT$)"),
        Column("BILL_AMT6", Integer, nullable=False, comment="Bill statement amount Apr 2005 (NT$)"),
        Column("PAY_AMT1", Integer, nullable=False, comment="Payment amount Sep 2005 (NT$)"),
        Column("PAY_AMT2", Integer, nullable=False, comment="Payment amount Aug 2005 (NT$)"),
        Column("PAY_AMT3", Integer, nullable=False, comment="Payment amount Jul 2005 (NT$)"),
        Column("PAY_AMT4", Integer, nullable=False, comment="Payment amount Jun 2005 (NT$)"),
        Column("PAY_AMT5", Integer, nullable=False, comment="Payment amount May 2005 (NT$)"),
        Column("PAY_AMT6", Integer, nullable=False, comment="Payment amount Apr 2005 (NT$)"),
        Column("DEFAULT", Integer, nullable=False, comment="Target: 1=Default, 0=No Default"),
        
        # Analytical Indexes for Query Optimization in MySQL
        Index("idx_default", "DEFAULT"),
        Index("idx_pay0", "PAY_0"),
        Index("idx_education", "EDUCATION"),
        Index("idx_age", "AGE"),
        Index("idx_limit_bal", "LIMIT_BAL"),
        Index("idx_composite_risk", "PAY_0", "LIMIT_BAL", "DEFAULT")
    )

    metadata.create_all(engine)
    print("[create_schema] Table `credit_card_clients` schema and indexes verified in MySQL.")


def load_data_to_mysql(engine: Engine, csv_path: str = PROCESSED_CSV, if_exists: str = "replace") -> int:
    """
    Ingest clean CSV dataset into MySQL table `credit_card_clients`.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Cleaned CSV not found at: {csv_path}")

    print(f"[load_data_to_mysql] Reading clean data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Write to MySQL table
    df.to_sql("credit_card_clients", engine, index=False, if_exists=if_exists, chunksize=5000)
    
    # Verify row count directly from MySQL
    with engine.connect() as conn:
        row_count = conn.execute(text("SELECT COUNT(*) FROM credit_card_clients")).scalar()
        col_count = len(df.columns)
    
    print(f"[load_data_to_mysql] Successfully verified {row_count:,} rows and {col_count} columns in MySQL.")
    return row_count


def execute_query(engine: Engine, sql_query: str) -> pd.DataFrame:
    """
    Execute a single SQL query against MySQL and return the result as a pandas DataFrame.
    """
    with engine.connect() as connection:
        result_df = pd.read_sql_query(text(sql_query), connection)
    return result_df


def parse_sql_file(sql_file_path: str = SQL_QUERIES_FILE) -> list:
    """
    Parse sql/analytics_queries.sql into individual named query blocks.
    """
    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"SQL file not found at: {sql_file_path}")

    with open(sql_file_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    pattern = r"-- QUERY\s+(\d+):\s+([^\n]+)"
    matches = list(re.finditer(pattern, full_text))
    
    queries = []
    for i, match in enumerate(matches):
        q_id = match.group(1)
        q_title = match.group(2).strip()
        start_pos = match.end()
        end_pos = matches[i+1].start() if i + 1 < len(matches) else len(full_text)
        
        chunk = full_text[start_pos:end_pos]
        sql_lines = [line for line in chunk.split("\n") if line.strip() and not line.strip().startswith("--")]
        sql_query = "\n".join(sql_lines).strip().rstrip(";")
        
        if sql_query:
            queries.append((f"QUERY {q_id}: {q_title}", sql_query))

    return queries


def run_all_queries_on_mysql(engine: Engine, sql_file_path: str = SQL_QUERIES_FILE) -> int:
    """
    Execute all 10 analytical queries against the live MySQL server and display results.
    """
    queries = parse_sql_file(sql_file_path)
    print(f"\n[run_all_queries_on_mysql] Executing {len(queries)} analytical queries against MySQL Server...")

    success_count = 0
    for idx, (title, query_str) in enumerate(queries, 1):
        print("\n" + "=" * 80)
        print(f"[{idx}/{len(queries)}] {title}")
        print("=" * 80)
        try:
            res_df = execute_query(engine, query_str)
            print(res_df.to_string(index=False))
            success_count += 1
        except Exception as e:
            print(f"Error executing {title} on MySQL: {e}")
            raise e

    print("\n" + "=" * 80)
    print(f"All {success_count}/{len(queries)} analytical queries executed successfully on MySQL Server 8.0.")
    print("=" * 80 + "\n")
    return success_count


def main():
    print("=" * 80)
    print("Banking Credit Risk — Phase 4 MySQL Production Pipeline")
    print("=" * 80)

    # 1. Connect to MySQL 8.0
    engine = get_mysql_engine()
    info = verify_mysql_connection(engine)

    # 2. Ingest 30,000 records
    load_data_to_mysql(engine, PROCESSED_CSV, if_exists="replace")

    # 3. Execute all 10 analytical queries
    run_all_queries_on_mysql(engine, SQL_QUERIES_FILE)


if __name__ == "__main__":
    main()