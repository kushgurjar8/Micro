from pydantic import BaseModel
from typing import Literal


class student(BaseModel):
    id: int
    name: str
    email: str
    password: str


class Login(BaseModel):
    email: str
    password: str


class branch(BaseModel):
    id: int
    name: str
    address: str | None = None
    phone: str | None = None


class employee(BaseModel):
    id: int
    name: str
    email: str
    password: str
    phone: str
    role: Literal["admin", "manager", "mentor", "employee"]
    branch_id: int             # ← changed from `branch: str`


class EmpLogin(BaseModel):
    email: str
    password: str