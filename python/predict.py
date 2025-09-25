#!/usr/bin/env python3
"""
ML Prediction Pipeline for Smart Health Surveillance.
- Fetches data from Postgres every 60 seconds
- Aggregates features per district and date
- Detects anomalies (Isolation Forest) and forecasts trends (Prophet)
- Inserts results into AggregatedSummary
"""

import os
import time
import json
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dateutil import parser as dtparser
from sklearn.ensemble import IsolationForest
from prophet import Prophet
import joblib
from dotenv import load_dotenv

# ---------- LOAD ENV ----------
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
MODEL_FILE = "outbreak_model.joblib"

if not DB_URL:
    raise RuntimeError("DATABASE_URL not set in environment")

# ---------- DB Helpers ----------
def get_db_conn():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    return conn

def fetch_table(conn, table):
    return pd.read_sql(f'SELECT * FROM "{table}"', conn)

def parse_datetime_safe(v):
    if pd.isna(v):
        return None
    if isinstance(v, pd.Timestamp):
        return v
    try:
        return dtparser.parse(str(v))
    except Exception:
        return None

# ---------- Aggregation ----------
def aggregate_data(h_df, p_df, s_df):
    h_df["date"] = h_df["visitDate"].apply(lambda x: parse_datetime_safe(x).date())
    p_df["date"] = p_df["saleDate"].apply(lambda x: parse_datetime_safe(x).date())
    s_df["date"] = s_df["timeStamp"].apply(lambda x: parse_datetime_safe(x).date())

    hosp_agg = h_df.groupby(["district","date"]).agg(
        hospitalCaseCount=("patientId","count"),
        severeCaseCount=("severity", lambda s: (s=="High").sum())
    ).reset_index()

    pharma_agg = p_df.groupby(["district","date"]).agg(
        pharmaSalesCount=("qtySold","sum")
    ).reset_index()

    social_agg = s_df.groupby(["district","date"]).agg(
        socialPostsCount=("postId","count"),
        negativePostsCount=("sentiment", lambda s: (s=="Negative").sum())
    ).reset_index()

    agg = hosp_agg.merge(pharma_agg, how="outer", on=["district","date"]) \
                  .merge(social_agg, how="outer", on=["district","date"]).fillna(0)

    return agg

# ---------- ML Prediction ----------
def predict_and_save(agg_df, conn):
    if not os.path.exists(MODEL_FILE):
        print("Model not found. Train the model first.")
        return

    iso_forest = joblib.load(MODEL_FILE)
    results = []

    for district in agg_df["district"].unique():
        df = agg_df[agg_df["district"]==district].sort_values("date").reset_index(drop=True)
        features = ["hospitalCaseCount","severeCaseCount","pharmaSalesCount",
                    "socialPostsCount","negativePostsCount"]

        X = df[features]
        df["is_anomaly"] = iso_forest.predict(X)
        df["is_anomaly"] = df["is_anomaly"].apply(lambda x: 1 if x==-1 else 0)

        # Forecast hospital cases with Prophet
        forecast_df = df[["date","hospitalCaseCount"]].rename(columns={"date":"ds","hospitalCaseCount":"y"})
        m = Prophet(daily_seasonality=True)
        m.fit(forecast_df)
        future = m.make_future_dataframe(periods=2)
        forecast = m.predict(future)
        future_cases = forecast["yhat"].iloc[-1]

        latest = df.iloc[-1]
        outbreak_score = 0.0
        risk_label = "Low"
        explanation = "Normal trends detected."

        recent_avg = df["hospitalCaseCount"].tail(7).mean()
        if latest["is_anomaly"]==1:
            outbreak_score += 0.5
            explanation = "Anomalous spike detected."
            if latest["hospitalCaseCount"] > recent_avg*1.5:
                outbreak_score += 0.2
                explanation += f" ({latest['hospitalCaseCount']:.0f} cases, {((latest['hospitalCaseCount']-recent_avg)/recent_avg*100):.0f}% rise)"
            if latest["negativePostsCount"] > df["negativePostsCount"].tail(7).mean()*1.5:
                outbreak_score += 0.2
                explanation += " and negative social posts spike"

        if future_cases > latest["hospitalCaseCount"]*1.5:
            outbreak_score += 0.1
            explanation += f" - Forecast predicts rise to {future_cases:.0f} cases."

        outbreak_score = min(1.0, max(0.0, outbreak_score))
        if outbreak_score>0.7:
            risk_label="High"
        elif outbreak_score>0.4:
            risk_label="Medium"

        results.append({
            "district": district,
            "date": latest["date"],
            "hospitalCaseCount": int(latest["hospitalCaseCount"]),
            "severeCaseCount": int(latest["severeCaseCount"]),
            "pharmaSalesCount": int(latest["pharmaSalesCount"]),
            "socialPostsCount": int(latest["socialPostsCount"]),
            "negativePostsCount": int(latest["negativePostsCount"]),
            "outbreakRiskScore": round(outbreak_score,2),
            "alertLevel": risk_label,
            "explanation": explanation
        })

    # Upsert into AggregatedSummary
    with conn.cursor() as cur:
        cur.execute('DELETE FROM "AggregatedSummary"')
        rows = [(r["district"], r["date"], r["hospitalCaseCount"], r["severeCaseCount"],
                 r["pharmaSalesCount"], r["socialPostsCount"], r["negativePostsCount"],
                 r["outbreakRiskScore"], r["alertLevel"]) for r in results]
        execute_values(cur, f"""
            INSERT INTO "AggregatedSummary"
            ("district","date","hospitalCaseCount","severeCaseCount","pharmaSalesCount",
            "socialPostsCount","negativePostsCount","outbreakRiskScore","alertLevel")
            VALUES %s
        """, rows)
    conn.commit()
    print(f"[{pd.Timestamp.now()}] AggregatedSummary updated for {len(results)} districts.")

# ---------- MAIN LOOP ----------
def main():
    try:
        conn = get_db_conn()
        h_df = fetch_table(conn, "HospitalRecord")
        p_df = fetch_table(conn, "PharmaSale")
        s_df = fetch_table(conn, "SocialPost")

        agg_df = aggregate_data(h_df,p_df,s_df)
        predict_and_save(agg_df, conn)

    except Exception as e:
        print(f"Prediction pipeline failed: {e}")
    finally:
        conn.close()

if __name__=="__main__":
    main()
