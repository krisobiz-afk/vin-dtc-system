
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    vin = Column(String, index=True)
    label = Column(String)
    comment = Column(String, default="")  # 👈 добавено
    upload_date = Column(DateTime, default=datetime.utcnow)

    modules = relationship("Module", back_populates="vehicle")
    errors = relationship("DTCError", back_populates="vehicle")



class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    part_number = Column(String)
    calibration_level = Column(String)
    strategy = Column(String)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))

    vehicle = relationship("Vehicle", back_populates="modules")

class DTCError(Base):
    __tablename__ = "dtc_errors"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String)
    description = Column(String)
    status = Column(String)
    date_detected = Column(DateTime, default=datetime.utcnow)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))

    vehicle = relationship("Vehicle", back_populates="errors")
