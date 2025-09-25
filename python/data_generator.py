import pandas as pd
import random
import os
from datetime import datetime, timedelta


# Random date in last 30 days (ISO format)
def random_date():
    today = datetime.now()
    start = today - timedelta(days=30)
    random_days = random.randint(0, 30)
    dt = start + timedelta(days=random_days, hours=random.randint(0,23), minutes=random.randint(0,59))
    return dt.isoformat(timespec="seconds")

# Spike
def add_spike(base, spike_prob=0.2, spike_range=(10, 50)):
    if random.random() < spike_prob:
        return base + random.randint(*spike_range)
    return base

# Disease -> Symptoms mapping
disease_symptoms = {
    "Cholera": ["Severe dehydration", "Watery diarrhea", "Vomiting", "Muscle cramps"],
    "Typhoid": ["Fever", "Abdominal pain", "Headache", "Weakness"],
    "Hepatitis A": ["Jaundice", "Fatigue", "Nausea", "Dark urine"],
    "Diarrhea": ["Loose stools", "Stomach cramps", "Dehydration"],
    "Dysentery": ["Bloody diarrhea", "Fever", "Abdominal pain"]
}

# Medicine mapping
medicine_disease_map = {
    "ORS": "Diarrhea",
    "Antibiotics": "Typhoid",
    "Paracetamol": "Fever",
    "Probiotics": "Dysentery",
    "Electrolyte Powder": "Cholera",
    "Anti-diarrheal": "Diarrhea"
}

# Medicines
medicines = list(medicine_disease_map.keys())

# Social media templates
social_templates = [
    "People in {district} complaining about dirty water and cases of {disease}.",
    "Hospitals in {district} are seeing more patients with {disease}.",
    "Is the water safe in {district}? Many have symptoms like {symptom}.",
    "Awareness camp in {district} about preventing {disease}.",
    "Shortage of {medicine} reported in {district} pharmacies.",
    "Rumors spreading on WhatsApp in {district} about unsafe drinking water."
]

# Districts
districts = [
    "Kamrup", "Dibrugarh", "Jorhat", "Barpeta", "Cachar", "Sonitpur",
    "East Khasi Hills", "West Khasi Hills", "Ri-Bhoi", "Shillong",
    "Imphal East", "Imphal West", "Aizawl", "Kohima", "Mokokchung"
]

# Hotspot districts for spikes
hotspots = ["Kamrup", "Dibrugarh"]

# Gender & reporting sources
genders = ["Male", "Female", "Other"]
report_sources = ["ASHA Worker", "Clinic", "Hospital"]
outcomes = ["Recovered", "Hospitalized", "Deceased"]

# Hospital Data
hospital_data = []
for i in range(1500):
    district = random.choice(districts)
    disease = random.choice(list(disease_symptoms.keys()))
    symptom = random.choice(disease_symptoms[disease])
    severity = random.choice(["Low", "Medium", "High"])

    if district in hotspots:
        severity = random.choices(["Medium", "High"], weights=[0.4, 0.6])[0]

    hospital_data.append({
        "patientId": f"P{i+1:04d}",
        "district": district,
        "hospitalId": f"H{random.randint(100,999)}",
        "doctorId": f"D{random.randint(1000,9999)}",
        "age": random.randint(1, 90),
        "gender": random.choice(genders),
        "symptoms": symptom,
        "diagnosis": disease,
        "severity": severity,
        "reportedBy": random.choice(report_sources),
        "outcome": random.choice(outcomes),
        "visitDate": random_date()
    })

# Pharma Sales Data
pharma_data = []
pharmacy_types = ["Rural", "Urban", "Govt", "Private"]

for i in range(1200):
    district = random.choice(districts)
    medicine = random.choice(medicines)
    qty = random.randint(1, 50)

    if district in hotspots:
        qty = add_spike(qty, spike_prob=0.3, spike_range=(20, 100))

    pharma_data.append({
        "pharmacyId": f"PH{random.randint(100,999)}",
        "district": district,
        "medicine": medicine,
        "diseaseTarget": medicine_disease_map[medicine],
        "qtySold": qty,
        "price": round(random.uniform(10, 500), 2),
        "pharmacyType": random.choice(pharmacy_types),
        "saleDate": random_date()
    })

# Social Media / News Posts
social_data = []
sentiments = ["Positive", "Neutral", "Negative"]
reaches = ["Low", "Medium", "High"]

for i in range(500):
    district = random.choice(districts)
    disease = random.choice(list(disease_symptoms.keys()))
    symptom = random.choice(disease_symptoms[disease])
    medicine = random.choice(medicines)
    template = random.choice(social_templates)

    if district in hotspots and random.random() < 0.4:
        template = "🚨 Outbreak alert! Many people in {district} are suffering from {disease}, showing {symptom}."

    content = template.format(district=district, disease=disease, symptom=symptom, medicine=medicine)

    social_data.append({
        "postId": f"S{i+1:04d}",
        "district": district,
        "platform": random.choice(["Twitter", "Facebook", "News", "Whatsapp", "Forum"]),
        "content": content,
        "sentiment": random.choice(sentiments),
        "reach": random.choice(reaches),
        "timeStamp": random_date()
    })

if not os.path.exists("data"):
    os.makedirs("data")

# Save CSVs
pd.DataFrame(hospital_data).to_csv("data/Hospital_Data.csv", index=False)
pd.DataFrame(pharma_data).to_csv("data/Pharma_Sales_Data.csv", index=False)
pd.DataFrame(social_data).to_csv("data/Social_Posts_Data.csv", index=False)

print("Synthetic Data Generated: Hospital_Data.csv, Pharma_Sales_Data.csv, Social_Posts_Data.csv")