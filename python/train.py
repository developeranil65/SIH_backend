
import pandas as pd
from sklearn.ensemble import IsolationForest
from prophet import Prophet
import numpy as np
import json
import os
import joblib

MODEL_FILE = "outbreak_model.joblib"

def load_and_aggregate_data():
    
    print("Loading and aggregating data from CSV files...")
    
    try:
        hospital_df = pd.read_csv("data/Hospital_Data.csv")
        pharma_df = pd.read_csv("data/Pharma_Sales_Data.csv")
        social_df = pd.read_csv("data/Social_Posts_Data.csv")
    except FileNotFoundError:
        print("Error: The 'data' directory or CSV files were not found.")
        print("Please run your 'data_generator.py' script first to create the data.")
        return None

    hospital_df['date'] = pd.to_datetime(hospital_df['visitDate']).dt.date
    pharma_df['date'] = pd.to_datetime(pharma_df['saleDate']).dt.date
    social_df['date'] = pd.to_datetime(social_df['timeStamp']).dt.date

    hospital_agg = hospital_df.groupby(['date', 'district']).agg(
        hospitalCaseCount=('patientId', 'count'),
        severeCaseCount=('severity', lambda x: (x == 'High').sum())
    ).reset_index()

    pharma_agg = pharma_df.groupby(['date', 'district']).agg(
        pharmaSalesCount=('qtySold', 'sum')
    ).reset_index()
    
    social_agg = social_df.groupby(['date', 'district']).agg(
        socialPostsCount=('postId', 'count'),
        negativePostsCount=('sentiment', lambda x: (x == 'Negative').sum())
    ).reset_index()

    merged_df = pd.merge(hospital_agg, pharma_agg, on=['date', 'district'], how='outer').fillna(0)
    merged_df = pd.merge(merged_df, social_agg, on=['date', 'district'], how='outer').fillna(0)
    
    all_dates = pd.date_range(start=merged_df['date'].min(), end=merged_df['date'].max()).date
    all_districts = merged_df['district'].unique()
    
    full_index = pd.MultiIndex.from_product([all_dates, all_districts], names=['date', 'district'])
    merged_df = merged_df.set_index(['date', 'district']).reindex(full_index, fill_value=0).reset_index()

    return merged_df

def train_and_save_model(df):
    
    print("Training the Isolation Forest model and saving it...")
    
    features = ['hospitalCaseCount', 'severeCaseCount', 'pharmaSalesCount', 'socialPostsCount', 'negativePostsCount']
    X = df[features]
    iso_forest = IsolationForest(contamination=0.1, random_state=42)
    iso_forest.fit(X)
    
    joblib.dump(iso_forest, MODEL_FILE)
    print(f"Model trained and saved to {MODEL_FILE}")


def main():
    if not os.path.exists("data/Hospital_Data.csv"):
        print("Please run your 'data_generator.py' script first.")
        return

    aggregated_data = load_and_aggregate_data()
    
    if aggregated_data is not None:
        if not os.path.exists(MODEL_FILE):
            train_and_save_model(aggregated_data)
        
        print("model is ready for predictions. You can now run 'predict.py' to see anomaly detection in action.")
    

if __name__ == "__main__":
    main()
