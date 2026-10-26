from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    password = Column(String)
    email = Column(String, unique=True)


class Branch(Base):
    __tablename__ = "branches"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    address = Column(String)
    phone = Column(String)

    # one Branch → many Employees
    employees = relationship("Employee", back_populates="branch")


class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String)
    phone = Column(String)
    role = Column(String, nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"))     # ← the FK

    # each Employee → one Branch
    branch = relationship("Branch", back_populates="employees")