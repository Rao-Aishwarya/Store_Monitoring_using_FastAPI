import os
import uuid
from fastapi import BackgroundTasks, FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import pytz
from models import *
from db import *
import pandas as pd
from typing import List

import models

app = FastAPI()

# Initialize database models
models.Base.metadata.create_all(bind=engine)

#Load CSV file data
def load_csv_to_db():
    # Load the pre-uploaded CSV files
    store_status_df = pd.read_csv("./csv_files/store_status.csv")
    store_status_df.to_sql("store_status", con=engine, if_exists='replace', index=False)

    business_hours_df = pd.read_csv("./csv_files/business_hours.csv")
    business_hours_df.to_sql("business_hours", con=engine, if_exists='replace', index=False)

    store_timezone_df = pd.read_csv("./csv_files/store_timezone.csv")
    store_timezone_df.to_sql("store_timezone", con=engine, if_exists='replace', index=False)

load_csv_to_db()


# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to the Store Monitoring API"}

def generate_report(report_id: str, db: Session):
    # Retrieve data from the database using pandas
    store_status_df = pd.read_sql("store_status", engine)
    business_hours_df = pd.read_sql("business_hours", engine)
    store_timezone_df = pd.read_sql("store_timezone", engine)

    # Example: Process data to calculate uptime and downtime
    report_data = []
    for store_id in store_status_df['store_id'].unique():
        # Filter data for each store
        store_data = store_status_df[store_status_df['store_id'] == store_id]
        # Perform your uptime/downtime calculations here
        uptime_last_hour = 50  # placeholder
        uptime_last_day = 20   # placeholder
        uptime_last_week = 100  # placeholder
        downtime_last_hour = 10  # placeholder
        downtime_last_day = 4   # placeholder
        downtime_last_week = 20  # placeholder

        report_data.append({
            "store_id": store_id,
            "uptime_last_hour": uptime_last_hour,
            "uptime_last_day": uptime_last_day,
            "uptime_last_week": uptime_last_week,
            "downtime_last_hour": downtime_last_hour,
            "downtime_last_day": downtime_last_day,
            "downtime_last_week": downtime_last_week,
        })

    # Convert the list to a pandas DataFrame
    report_df = pd.DataFrame(report_data)

    # Generate the CSV file
    csv_filename = f"report_{report_id}.csv"
    csv_filepath = os.path.join(os.getcwd(), csv_filename)
    report_df.to_csv(csv_filepath, index=False)

    # Update the report status in the database
    report = db.query(Report).filter(Report.id == report_id).first()
    report.status = "Complete"
    report.file_path = csv_filepath
    db.commit()


@app.post("/trigger_report")
def trigger_report(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    report_id = str(uuid.uuid4())
    new_report = Report(id=report_id)
    db.add(new_report)
    db.commit()
    background_tasks.add_task(generate_report, report_id, db)
    return {"report_id": report_id}

@app.get("/get_report/{report_id}")
def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.status == "Running":
        return {"status": "Running"}
    
    return {"status": "Complete", "csv_file": report.file_path}


