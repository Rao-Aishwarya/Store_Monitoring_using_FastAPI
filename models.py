from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
import pandas as pd
from db import *


# Define the database models
class StoreStatus(Base):
    __tablename__ = "store_status"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, index=True)
    timestamp_utc = Column(DateTime, index=True)
    status = Column(String)

class BusinessHours(Base):
    __tablename__ = "business_hours"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, index=True)
    day_of_week = Column(Integer)
    start_time_local = Column(String)
    end_time_local = Column(String)

class StoreTimezone(Base):
    __tablename__ = "store_timezone"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, index=True)
    timezone_str = Column(String)

class Report(Base):
    __tablename__ = "reports"
    id = Column(String, primary_key=True, index=True)
    status = Column(String, default="Running")
    created_at = Column(DateTime, default=func.now())
    file_path = Column(String, nullable=True)

