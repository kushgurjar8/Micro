# ---------------------------------Imports---------------------------------

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import jwt
import bcrypt

from models import *
from database import engine, SessionLocal, Base
import database_models

import os


# ---------------------------------Setup---------------------------------

app = FastAPI()
Base.metadata.create_all(bind=engine)     # creates the tables if they don't exist

SECURITY_KEY = os.environ.get("JWT_SECRET", "dev-only-insecure-key")
ALGORITHM = "HS256"


# ---------------------------------Helpers---------------------------------

# opens a DB session for each request and closes it afterwards
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# turn a plain password into a hash before saving it
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


# check if the typed password matches the saved hash
def verify_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


# ---------------------------------Middleware---------------------------------

# runs on every request
@app.middleware("http")
async def my_middleware(request: Request, call_next):
    print("Request:", request.method, request.url.path)
    response = await call_next(request)
    print("Response:", response.status_code)
    return response


#    def (regular / sync):
   
#    ├─ query the DB  ──────► waits 2 sec ◄──── nothing else can happen
#    ├─ format result                              during this wait
#    └─ return
   
   
#    async def:
   
#    ├─ await DB      ──────► waits 2 sec ◄──── OTHER requests
#    │                                            can be handled 
#    │                                            during this wait
#    ├─ format result
#    └─ return

# ---------------------------------Welcome---------------------------------

@app.get("/")
def get_data():
    return "Welcome to FastAPI"


# ---------------------------------Students CRUD---------------------------------

# read all
@app.get("/student/", tags=["Students"])
def get_students(db: Session = Depends(get_db)):
    return db.query(database_models.Student).all()


# read one
@app.get("/student_id/{id}", tags=["Students"])
def get_student(id: int, db: Session = Depends(get_db)):
    s = db.get(database_models.Student, id)
    if s:
        return s
    return "Student not found"


# create
@app.post("/student_create/", tags=["Students"])
def add_student(new_student: student, db: Session = Depends(get_db)):
    if db.get(database_models.Student, new_student.id):
        return "Student already exists"

    email_taken = db.query(database_models.Student).filter(
        database_models.Student.email == new_student.email
    ).first()
    if email_taken:
        return "Email already registered"

    data = new_student.model_dump()
    data["password"] = hash_password(new_student.password)
    db.add(database_models.Student(**data))
    db.commit()
    return "Student created"


# update
@app.put("/student_update/{id}", tags=["Students"])
def update_student(id: int, updated_student: student, db: Session = Depends(get_db)):
    s = db.get(database_models.Student, id)
    if s:
        s.name = updated_student.name
        s.email = updated_student.email
        s.password = hash_password(updated_student.password)
        db.commit()
        return "Student updated"
    return "Student not found"


# delete
@app.delete("/student_delete/{id}", tags=["Students"])
def delete_student(id: int, db: Session = Depends(get_db)):
    s = db.get(database_models.Student, id)
    if s:
        db.delete(s)
        db.commit()
        return "Student deleted"
    return "Student not found"


# ---------------------------------Students Login---------------------------------

@app.post("/login", tags=["Students Login"])
def login(data: Login, db: Session = Depends(get_db)):
    student = db.query(database_models.Student).filter(
        database_models.Student.email == data.email
    ).first()

    if student is None or not verify_password(data.password, student.password):
        raise HTTPException(status_code=404, detail="Invalid email or password")

    payload = {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    token = jwt.encode(payload, SECURITY_KEY, algorithm=ALGORITHM)
    return {"message": "Login successful", "access_token": token}


# ---------------------------------Role Based Access Control (Employees)---------------------------------

bearer = HTTPBearer()     # reads "Authorization: Bearer <token>" + adds the Authorize button


# check the token and the role (only admin and manager pass)
def admin_or_manager(creds = Depends(bearer)):
    try:
        payload = jwt.decode(creds.credentials, SECURITY_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if payload.get("role") not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only admin and manager are allowed")

    return payload


# check a token that the DRF service signed (only for the endpoints other services call)
DRF_ISSUER = "drf-service"

def drf_user(creds = Depends(bearer)):
    try:
        payload = jwt.decode(
            creds.credentials,
            SECURITY_KEY,                 # the same JWT_SECRET that DRF signs with
            algorithms=[ALGORITHM],
            issuer=DRF_ISSUER,            # reject tokens that DRF did not issue
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("token_type") != "access":
        raise HTTPException(status_code=401, detail="Access token required")

    return payload

# ---------------------------------Employees Login---------------------------------

@app.post("/emp_login", tags=["Employees Login"])
def emp_login(data: EmpLogin, db: Session = Depends(get_db)):
    emp = db.query(database_models.Employee).filter(
        database_models.Employee.email == data.email
    ).first()
    if emp is None or not verify_password(data.password, emp.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    payload = {
        "id": emp.id,
        "role": emp.role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    token = jwt.encode(payload, SECURITY_KEY, algorithm=ALGORITHM)
    return {"message": "Login successful", "role": emp.role, "access_token": token}


# ---------------------------------Employees CRUD (only admin and manager)---------------------------------

# create
@app.post("/emp_create/", tags=["Employees"])
def emp_create(new_emp: employee, db: Session = Depends(get_db), user = Depends(admin_or_manager)):
    if db.get(database_models.Employee, new_emp.id):
        return "Employee already exists"
    data = new_emp.model_dump()
    data["password"] = hash_password(new_emp.password)
    db.add(database_models.Employee(**data))
    db.commit()
    return "Employee created"


# read all
@app.get("/emp_all/", tags=["Employees"])
def emp_all(db: Session = Depends(get_db), user = Depends(admin_or_manager)):
    return db.query(database_models.Employee).all()


# read one
@app.get("/emp_id/{id}", tags=["Employees"])
def emp_get(id: int, db: Session = Depends(get_db), user = Depends(admin_or_manager)):
    e = db.get(database_models.Employee, id)
    if e:
        return e
    return "Employee not found"


# update
@app.put("/emp_update/{id}", tags=["Employees"])
def emp_update(id: int, updated: employee, db: Session = Depends(get_db), user = Depends(admin_or_manager)):
    e = db.get(database_models.Employee, id)
    if e:
        e.name = updated.name
        e.email = updated.email
        e.password = hash_password(updated.password)
        e.phone = updated.phone
        e.role = updated.role
        e.branch_id = updated.branch_id
        db.commit()
        return "Employee updated"
    return "Employee not found"


# delete
@app.delete("/emp_delete/{id}", tags=["Employees"])
def emp_delete(id: int, db: Session = Depends(get_db), user = Depends(admin_or_manager)):
    e = db.get(database_models.Employee, id)
    if e:
        db.delete(e)
        db.commit()
        return "Employee deleted"
    return "Employee not found"


# ---------------------------------Branches CRUD (admin and manager only)---------------------------------

# create
@app.post("/branch_create/", tags=["Branches"])
def branch_create(new_br: branch, db: Session = Depends(get_db), user = Depends(admin_or_manager)):
    if db.get(database_models.Branch, new_br.id):
        return "Branch already exists"
    db.add(database_models.Branch(**new_br.model_dump()))
    db.commit()
    return "Branch created"


# read all
@app.get("/branch_all/", tags=["Branches"])
def branch_all(db: Session = Depends(get_db), user = Depends(admin_or_manager)):
    return db.query(database_models.Branch).all()


# read one — WITH its employees (shows off the relationship!)
@app.get("/branch_id/{id}", tags=["Branches"])
def branch_get(id: int, db: Session = Depends(get_db), user = Depends(admin_or_manager)):
    b = db.get(database_models.Branch, id)
    if b is None:
        return "Branch not found"
    return {
        "id": b.id,
        "name": b.name,
        "address": b.address,
        "phone": b.phone,
        "employees": [                                       # ← b.employees comes from relationship()
            {"id": e.id, "name": e.name, "role": e.role}
            for e in b.employees
        ],
    }


# update
@app.put("/branch_update/{id}", tags=["Branches"])
def branch_update(id: int, updated: branch, db: Session = Depends(get_db), user = Depends(admin_or_manager)):
    b = db.get(database_models.Branch, id)
    if b:
        b.name = updated.name
        b.address = updated.address
        b.phone = updated.phone
        db.commit()
        return "Branch updated"
    return "Branch not found"


# delete
@app.delete("/branch_delete/{id}", tags=["Branches"])
def branch_delete(id: int, db: Session = Depends(get_db), user = Depends(admin_or_manager)):
    b = db.get(database_models.Branch, id)
    if b:
        db.delete(b)
        db.commit()
        return "Branch deleted"
    return "Branch not found"


# employee + branch info nested (shows the OTHER side of the relationship)
@app.get("/emp_full/{id}", tags=["Employees"])
def emp_full(id: int, db: Session = Depends(get_db), user = Depends(admin_or_manager)):
    e = db.get(database_models.Employee, id)
    if e is None:
        return "Employee not found"
    return {
        "id": e.id,
        "name": e.name,
        "email": e.email,
        "role": e.role,
        "phone": e.phone,
        "branch": {                                      # ← e.branch comes from relationship()
            "id": e.branch.id,
            "name": e.branch.name,
            "address": e.branch.address,
            "phone": e.branch.phone,
        } if e.branch else None,
    }



# ---------------------------------For DRF Service---------------------------------




# list of students for other services (no passwords)
@app.get("/service/students/", tags=["DRF Service"])
def service_students(db: Session = Depends(get_db), user = Depends(drf_user)):
    return [
        {"id": s.id, "name": s.name, "email": s.email}
        for s in db.query(database_models.Student).all()
    ]


# one mentor (an employee with role "mentor") for other services
@app.get("/mentor/{id}", tags=["DRF Service"])
def get_mentor(id: int, db: Session = Depends(get_db), user = Depends(drf_user)):
    m = db.get(database_models.Employee, id)
    if m is None or m.role != "mentor":
        raise HTTPException(status_code=404, detail="Mentor not found")
    return {"id": m.id, "name": m.name, "email": m.email, "phone": m.phone}
