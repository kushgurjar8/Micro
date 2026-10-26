# @app.get('/')
# def get_data():
#     return " Welcome to FastAPI"

# students = [
#     student(id= 1, name= 'kush'),
#     student(id= 2, name= 'kiran'),
#     student(id= 3, name= 'gaurav'),
#     ]

# @app.get("/student/")
# def get_students():
#     return students

# get student by id(crud without db) :

# @app.get("/student_id/{id}")
# def get_student(id: int):
#     for s in students:
#         if s.id == id:
#             return s
#     return "Student not found"

# create a student(crud without db):

# @app.post("/student_create/")
# def add_student(new_student: student):
#     for s in students:
#         if s.id == new_student.id:
#             return "Student already exists"
#     students.append(new_student)
#     return new_student


# update a student(crud without db) :

# @app.put("/student_update/{id}")
# def update_student(id: int, updated_student: student):
#     for i in range(len(students)):
#         if students[i].id == id:
#             students[i] = updated_student
#             return updated_student
#     return "Student not found"

# delete a student(crud without db) : 

# @app.delete("/student_delete/{id}")
# def delete_student(id: int):
#     for i in range(len(students)):
#         if students[i].id == id:
#             del students[i]
#             return "Student deleted"
#     return "Student not found"


# create a student

# @app.post("/student_create/",tags=["Students"])
# def add_student(new_student: student, db: Session = Depends(get_db)):
#     if db.get(database_models.Student, new_student.id):
#         return "Student already exists"
#     db.add(database_models.Student(**new_student.model_dump()))
#     db.commit()
#     return new_student

# one more method to create if we dont want to use **new_student.modeldump()

# @app.post("/student_create/",tags=["Students"])
# def add_student(new_student: student, db: Session = Depends(get_db)):
#     if db.get(database_models.Student, new_student.id):
#         return "Student already exists"

#     db_student = database_models.Student(
#         id=new_student.id,
#         name=new_student.name
#     )
#     db.add(db_student)
#     db.commit()
#     return new_student


# update a student

# @app.put("/student_update/{id}",tags=["Students"])
# def update_student(id: int, updated_student: student, db: Session = Depends(get_db)):
#     s = db.get(database_models.Student, id)
#     if s:
#         s.name = updated_student.name
#         s.password = updated_student.password     
#         db.commit()
#         db.refresh(s)                             
#         return s                                  
#     return "Student not found"



# login JWT

# @app.post("/login", tags=["Login"])
# def login(data: Login, db: Session = Depends(get_db)):
#     student = db.query(database_models.Student).filter(
#         database_models.Student.name == data.username
#     ).first()

#     if student is None or student.password != data.password:
#         raise HTTPException(status_code=404, detail="Invalid username or password")

#     payload = {
#         "id": student.id,
#         "name": student.name,
#         "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
#     }

#     token = jwt.encode(payload, SECURITY_KEY, algorithm=ALGORITHM)

#     return {"message": "Login successful", "access_token": token}


 # -------------------without password hashing-----------------

    # if student is None or student.password != data.password:
    #     raise HTTPException(status_code=404, detail="Invalid email or password")


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






# database_models.py(before relation b/w tables) : 

# from sqlalchemy import Column, Integer, String
# from database import Base

# class Student(Base):
#     __tablename__ = "students"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     password = Column(String)
#     email = Column(String, unique=True)


# class Employee(Base):
#     __tablename__ = "employees"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     email = Column(String, unique=True, nullable=False)
#     password = Column(String, nullable=False)
#     phone = Column(String)
#     role = Column(String, nullable=False)
#     branch = Column(String)


# models.py(before relation b/w tables) : 

# from pydantic import BaseModel

# from typing import Literal


# # ----------------------------model for login with username----------------------
# # class student(BaseModel):
# #     id: int
# #     name: str
# #     password: str

# # class Login(BaseModel):
# #     username: str
# #     password: str

# # --------------------------------model for login with email-----------------------

# class student(BaseModel):
#     id: int
#     name: str
#     email: str    
#     password: str

# class Login(BaseModel):
#     email: str           
#     password: str


# # --------------------------------model for RBAC--------------------------------------  


# class employee(BaseModel):
#     id: int
#     name: str
#     email: str
#     password: str
#     phone: str
#     role: Literal["admin", "manager", "mentor", "employee"]
#     branch: str

# class EmpLogin(BaseModel):
#     email: str
#     password: str