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

# Expanded Districts
districts = [
    "Kamrup", "Dibrugarh", "Jorhat", "Barpeta", "Cachar", "Sonitpur",
    "East Khasi Hills", "West Khasi Hills", "Ri-Bhoi", "Shillong",
    "Imphal East", "Imphal West", "Aizawl", "Kohima", "Mokokchung",
    "Tinsukia", "Nagaon", "Golaghat", "Karimganj", "Hailakandi",
    "Dimapur", "Mon", "Ukhrul", "Churachandpur", "Lunglei", "Saiha"
]

# Hotspot districts (higher outbreak probability)
hotspots = ["Kamrup", "Dibrugarh", "Barpeta", "Cachar", "Sonitpur", "Shillong", "Aizawl", "Nagaon"]

# Gender & reporting sources
genders = ["Male", "Female", "Other"]
report_sources = ["ASHA Worker", "Clinic", "Hospital"]
outcomes = ["Recovered", "Hospitalized", "Deceased"]

# ---------- DATA GENERATION SIZE ----------
NUM_HOSPITAL = 100000   # Hospital records
NUM_PHARMA = 40000      # Pharma sales records
NUM_SOCIAL = 10000      # Social posts

# ---------- OUTBREAK MODEL ----------
outbreak_districts = {}
for d in districts:
    # Hotspots: 70% chance of outbreak
    if d in hotspots:
        outbreak_districts[d] = random.random() < 0.7
    else:
        outbreak_districts[d] = random.random() < 0.3  # Non-hotspots can also suffer

# ---------- HOSPITAL DATA ----------
hospital_data = []
for i in range(NUM_HOSPITAL):
    district = random.choice(districts)
    disease = random.choice(list(disease_symptoms.keys()))
    symptom = random.choice(disease_symptoms[disease])

    # Severity depends on outbreak
    if outbreak_districts[district]:
        severity = random.choices(["Medium", "High"], weights=[0.4, 0.6])[0]
    else:
        severity = random.choice(["Low", "Medium"])

    hospital_data.append({
        "patientId": f"P{i+1:06d}",
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

# ---------- PHARMA SALES DATA ----------
pharma_data = []
pharmacy_types = ["Rural", "Urban", "Govt", "Private"]

for i in range(NUM_PHARMA):
    district = random.choice(districts)
    medicine = random.choice(medicines)
    qty = random.randint(1, 50)

    # Spike sales if outbreak is active
    if outbreak_districts[district]:
        qty = add_spike(qty, spike_prob=0.6, spike_range=(50, 200))

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

# ---------- SOCIAL MEDIA DATA ----------
social_data = []
sentiments = ["Positive", "Neutral", "Negative"]
reaches = ["Low", "Medium", "High"]

for i in range(NUM_SOCIAL):
    district = random.choice(districts)
    disease = random.choice(list(disease_symptoms.keys()))
    symptom = random.choice(disease_symptoms[disease])
    medicine = random.choice(medicines)

    if outbreak_districts[district]:
        template = "🚨 Outbreak alert! Many people in {district} are suffering from {disease}, showing {symptom}."
        sentiment = "Negative"
        reach = random.choices(reaches, weights=[0.2, 0.3, 0.5])[0]  # more High reach
    else:
        template = random.choice(social_templates)
        sentiment = random.choice(sentiments)
        reach = random.choice(reaches)

    content = template.format(district=district, disease=disease, symptom=symptom, medicine=medicine)

    social_data.append({
        "postId": f"S{i+1:05d}",
        "district": district,
        "platform": random.choice(["Twitter", "Facebook", "News", "Whatsapp", "Forum"]),
        "content": content,
        "sentiment": sentiment,
        "reach": reach,
        "timeStamp": random_date()
    })

# ---------- SAVE ----------
if not os.path.exists("data"):
    os.makedirs("data")

pd.DataFrame(hospital_data).to_csv("data/Hospital_Data.csv", index=False)
pd.DataFrame(pharma_data).to_csv("data/Pharma_Sales_Data.csv", index=False)
pd.DataFrame(social_data).to_csv("data/Social_Posts_Data.csv", index=False)

print(f"Synthetic Data Generated with {NUM_HOSPITAL + NUM_PHARMA + NUM_SOCIAL} rows")
print(f"Outbreak districts: {[d for d,v in outbreak_districts.items() if v]}")
