# Report generation for store monitoring using FastAPI, SQLAlchemy and SQLite

This repository contains a FastAPI application for monitoring store uptime and downtime based on pre-uploaded CSV files. The application uses SQLite for local storage and provides endpoints to generate and retrieve reports on store activity.

## Table of Contents
- [Setup](#setup)
- [Running the Application](#running-the-application)
- [Problem Statement](#problem-statement)

# Setup
## Prerequisites
Ensure you have the following software installed:

- Python 3.8 or higher
- pip (Python package installer)
- Git
- uvicorn
- sqlalchemy
```pip install uvicorn pymysql fastapi sqlalchemy```

## Installation
1. **Clone the Repository**

   ```bash
   git clone https://github.com/Rao-Aishwarya/Store_Monitoring_using_FastAPI.git
   cd your-repository

## Setup Virtual Environment
### Create and activate a virtual environment
1. On macOS/Linux
```
python3 -m venv venv
source venv/bin/activate
```

## Add CSV file
Place your CSV files in the ```csv_files``` directory:

store_status.csv - Contains store activity data
business_hours.csv - Contains store business hours
store_timezone.csv - Contains store timezones

## Configure Alembic (Optional)
- Install package alembic (for database migrations)
- Initialize it
- Create initial migration
- Apply migrations
```pip install alembic```
```alembic init alembic```
```alembic revision --autogenerate -m "Initial migration"```
```alembic upgrade head```

## Running the application
1. Start the FastAPI Server
```uvicorn main:app --reload```

2. Check the API Documentation
Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API documentation using Swagger UI.

## Problem statement

Company A monitors several restaurants in the US and needs to monitor if the store is online or not. All restaurants are supposed to be online during their business hours. Due to some unknown reasons, a store might go inactive for a few hours. Restaurant owners want to get a report of the how often this happened in the past.   

We want to build backend APIs that will help restaurant owners achieve this goal. 

The following data sources contain all the data that is required to achieve this purpose.

### Data sources

There are 3 sources of data 

1. Every store is polled roughly every hour and have data about whether the store was active or not in a CSV.  The CSV has 3 columns (`store_id, timestamp_utc, status`) where status is active or inactive.  All timestamps are in **UTC**

2. The business hours of all the stores - schema of this data is `store_id, dayOfWeek(0=Monday, 6=Sunday), start_time_local, end_time_local`
    1. These times are in the **local time zone**
    2. If data is missing for a store, assume it is open 24*7
       
3. Timezone for the stores - schema is `store_id, timezone_str` 
    1. If data is missing for a store, assume it is America/Chicago
    2. This is used so that data sources 1 and 2 can be compared against each other. 
All CSV files can be found [here](https://drive.google.com/drive/folders/19ij-zLcpeWUhpaWvfnckhEVzQ98Zr9Dc?usp=drive_link)


### Data output requirement

The output report generated and seen by the user has the following schema:

`store_id, uptime_last_hour(in minutes), uptime_last_day(in hours), update_last_week(in hours), downtime_last_hour(in minutes), downtime_last_day(in hours), downtime_last_week(in hours)` 

1. Uptime and downtime should only include observations within business hours. 
2. You need to extrapolate uptime and downtime based on the periodic polls we have ingested, to the entire time interval.
    1. eg, business hours for a store are 9 AM to 12 PM on Monday
        1. we only have 2 observations for this store on a particular date (Monday) in our data at 10:14 AM and 11:15 AM
        2. we need to fill the entire business hours interval with uptime and downtime from these 2 observations based on some sane interpolation logic


### API requirement

1. You need two APIs 
    1. /trigger_report endpoint that will trigger report generation from the data provided (stored in DB)
        1. No input 
        2. Output - report_id (random string) 
        3. report_id will be used for polling the status of report completion
    2. /get_report endpoint that will return the status of the report or the csv
        1. Input - report_id
        2. Output
            - if report generation is not complete, return “Running” as the output
            - if report generation is complete, return “Complete” along with the CSV file with the schema described above.


