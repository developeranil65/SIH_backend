#!/usr/bin/env python3
"""
ETL pipeline with periodic execution (every 60 sec).
Steps:
1. Run datagenerator.py to create fresh CSVs
2. Clear old data from Postgres tables
3. Insert new data from CSVs
"""

import os
import time
import subprocess
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dateutil import parser as dtparser
from dotenv import load_dotenv

# ---------- LOAD ENV ----------
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("DATABASE_URL not set in environment")

# ---------- CONFIG ----------
DATA_DIR = "data"
HOSPITAL_CSV = os.path.join(DATA_DIR, "Hospital_Data.csv")
PHARMA_CSV = os.path.join(DATA_DIR, "Pharma_Sales_Data.csv")
SOCIAL_CSV = os.path.join(DATA_DIR, "Social_Posts_Data.csv")

TBL_HOSPITAL = "HospitalRecord"
TBL_PHARMA   = "PharmaSale"
TBL_SOCIAL   = "SocialPost"

# ---------- HELPERS ----------
def get_db_conn():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    return conn

def parse_date_safe(v):
    if pd.isna(v):
        return None
    if isinstance(v, pd.Timestamp):
        return v
    try:
        return dtparser.parse(str(v))
    except Exception:
        return None

def normalize_df(df, date_col):
    if df.empty:
        return df
    df[date_col] = df[date_col].apply(parse_date_safe)
    df = df[df[date_col].notna()]
    return df

def load_csv(path):
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

def bulk_insert(conn, table, cols, rows):
    if not rows:
        return 0
    columns = ",".join([f'"{c}"' for c in cols])
    sql = f'INSERT INTO "{table}" ({columns}) VALUES %s'
    with conn.cursor() as cur:
        execute_values(cur, sql, rows, page_size=1000)
    return len(rows)

def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute(f'TRUNCATE TABLE "{TBL_HOSPITAL}" RESTART IDENTITY CASCADE')
        cur.execute(f'TRUNCATE TABLE "{TBL_PHARMA}" RESTART IDENTITY CASCADE')
        cur.execute(f'TRUNCATE TABLE "{TBL_SOCIAL}" RESTART IDENTITY CASCADE')
    conn.commit()
    print("✅ Old data cleared from tables")

# ---------- MAIN ETL ----------
def run_etl():
    print("⚙️ Running datagenerator.py ...")
    subprocess.run(["python", "data_generator.py"], check=True)

    print("📂 Loading CSVs...")
    h_df = normalize_df(load_csv(HOSPITAL_CSV), "visitDate")
    p_df = normalize_df(load_csv(PHARMA_CSV), "saleDate")
    s_df = normalize_df(load_csv(SOCIAL_CSV), "timeStamp")

    conn = get_db_conn()
    try:
        clear_tables(conn)

        # ---------- HospitalRecord ----------
        hospital_cols = ["patientId","district","hospitalId","doctorId","reportedBy","age",
                         "gender","symptoms","diagnosis","severity","outcome","visitDate"]
        inserted_h = bulk_insert(conn, TBL_HOSPITAL, hospital_cols,
                                 h_df[hospital_cols].values.tolist())

        # ---------- PharmaSale ----------
        pharma_cols = ["pharmacyId","district","medicine","diseaseTarget","qtySold",
                       "price","pharmacyType","saleDate"]
        inserted_p = bulk_insert(conn, TBL_PHARMA, pharma_cols,
                                 p_df[pharma_cols].values.tolist())

        # ---------- SocialPost ----------
        social_cols = ["postId","district","platform","content","sentiment","reach","timeStamp"]
        inserted_s = bulk_insert(conn, TBL_SOCIAL, social_cols,
                                 s_df[social_cols].values.tolist())

        conn.commit()
        print(f"✅ ETL complete: Hospital={inserted_h}, Pharma={inserted_p}, Social={inserted_s}")

    except Exception as e:
        conn.rollback()
        print(f"❌ ETL failed: {e}")
        raise
    finally:
        conn.close()

# ---------- LOOP ----------
if __name__ == "__main__":
    while True:
        try:
            run_etl()
            print("🤖 Running predict.py on fresh data...")
            subprocess.run(["python", "predict.py"], check=True)
            print("✅ Prediction complete")
        except Exception as e:
            print(f"Pipeline error: {e}")
        print("⏳ Waiting 40 seconds before next run...")
        time.sleep(40)
