import enum

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Enum, DECIMAL
from sqlalchemy.orm import relationship

from datetime import datetime

from database import Base

class GenderEnum(enum.Enum):
    """
    Table Enum Values
    - Male
    - Female
    """

    Male = "Male"
    Female = "Female"


class StatusEnum(enum.Enum):
    """
    Table Enum Values
    - Created
    - Complete
    - Canceled
    - Rescheduled
    """

    Created = "Created"
    Complete = "Complete"
    Canceled = "Canceled"
    Rescheduled = "Rescheduled"



class DoctorModel(Base):
    __tablename__ = "doctors"

    id = Column(String(36),  primary_key=True)
    first_name = Column(String(60))
    last_name = Column(String(60))
    email = Column(String(60))
    password = Column(String(255))
    number = Column(String(13))
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)


class SpecializationModel(Base):
    __tablename__ = "specializations"

    id = Column(String(36),  primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text(), nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)


class DoctorSpecializationModel(Base):
    __tablename__ = "doctor_specializations"

    id = Column(String(36),  primary_key=True)
    doctor_id = Column(String(36), ForeignKey("doctors.id"))
    specialization_id = Column(String(36), ForeignKey("specializations.id"))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    doctor = relationship("DoctorModel", backref="doctor_specializations")
    specialization = relationship("SpecializationModel", backref="doctor_specializations")


class PatientModel(Base):
    __tablename__ = "patients"

    id = Column(String(36),  primary_key=True)
    first_name = Column(String(60))
    last_name = Column(String(60))
    email = Column(String(60))
    password = Column(String(255))
    number = Column(String(13))
    gender = Column(Enum(GenderEnum), nullable=False)
    height = Column(DECIMAL(5, 2))
    weight = Column(DECIMAL(5, 2))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)


class AppointmentModel(Base):
    __tablename__ = "appointments"

    id = Column(String(36),  primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"))
    doctor_id = Column(String(36), ForeignKey("doctors.id"))
    from_time = Column(DateTime)
    to_time = Column(DateTime)
    status = Column(Enum(StatusEnum), nullable=False)
    canceller_id = Column(String(36), nullable=True)
    description = Column(Text(), nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    patient = relationship("PatientModel", backref="appointments")
    doctor = relationship("DoctorModel", backref="appointments")


class AdminUserModel(Base):
    __tablename__ = "admin_users"

    id = Column(String(36), primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(200))
    password = Column(String(255), default="0")
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
