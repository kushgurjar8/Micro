# FastAPI Learning — Setup & Code Reference

Project folder: `C:\Users\KUSH\Desktop\FastAPI`
Python: 3.14.6 (venv named `myenv`) · Editor: VS Code · Shell: PowerShell · DB: PostgreSQL 18 (`fastapi_db`), pgAdmin 4

---

## 1. Project structure (current — as of 17/10/26)

```
FastAPI/
├── myenv/               # virtual environment
├── database.py          # engine, SessionLocal, Base (DATABASE_URL)
├── database_models.py   # SQLAlchemy tables: Student  AND  Employee (id, name, email, password, phone, role, branch)
├── models.py            # Pydantic models: student, Login, employee, EmpLogin  (imported with `from models import *`)
└── main.py              # app, helpers, middleware, student routes, RBAC guard, employee routes
```

- `get_db` lives in **main.py**. Everything in main.py — no separate auth.py / routers.
- **Two tables**: `students` and `employees`. Students have the open `/login`; employees go through `/emp_login` and their CRUD is protected by RBAC (only admin + manager pass).

## 2. Create & activate the virtual environment (PowerShell)

```powershell
python -m venv myenv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\myenv\Scripts\Activate.ps1
```

## 3. Install packages

```powershell
pip install fastapi "uvicorn[standard]" sqlalchemy "psycopg[binary]" PyJWT bcrypt
```

## 4. Run the server

```powershell
uvicorn main:app --reload        # or: python -m uvicorn main:app --reload
```

- http://127.0.0.1:8000/docs — Swagger UI (grouped by `tags`: Students, Students Login, Employees, Employees Login)

---

## 5. main.py — file layout (top → bottom)

The file reads top-to-bottom in this order (everything a route needs is defined before the route uses it):

```
1. Imports
2. Setup                 → app, Base.metadata.create_all, SECURITY_KEY, ALGORITHM
3. Helpers               → get_db, hash_password, verify_password
4. Middleware            → my_middleware (runs on every request)
5. Welcome route         → GET /
6. Students CRUD         → 4 routes (read all / read one / create / update / delete)
7. Students Login        → POST /login
8. RBAC guard            → bearer + admin_or_manager
9. Employees Login       → POST /emp_login
10. Employees CRUD       → 5 routes (create / read all / read one / update / delete), all protected
```

---

## 6. CRUD style (the agreed method)

- One function per operation, action in the URL: `/student/`, `/student_id/{id}`, `/student_create/`, `/student_update/{id}`, `/student_delete/{id}` (same pattern for `/emp_*`)
- Pydantic models `student` / `employee` (lowercase) as request body; SQLAlchemy tables `database_models.Student` / `database_models.Employee`
- `db.get(Table, id)` to find by id; `db.query(Table).filter(Table.col == x).first()` for other columns
- Return plain string messages (`"Student not found"`, `"Employee created"`)
- Create: `**data` (from `model_dump()`) copies all fields automatically. Update: every field written by hand (`e.x = updated.x`)
- Every route uses `tags=["..."]` to group in Swagger UI

Adding a column checklist: pgAdmin `ALTER TABLE ... ADD COLUMN` (create_all never alters existing tables) → database_models.py → models.py → update function line.

---

## 7. Password hashing (bcrypt)

```python
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def verify_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False
```

- Hash on create/update, verify on login. Hashes can't be reversed.
- `SECURITY_KEY` must be a **fixed string** (sits in the Setup section at the top); `secrets.token_hex(32)` changes on every `--reload` and invalidates all tokens.

---

## 8. Role Based Access Control (Employees)

Separate `Employee` table with role column (`admin`, `manager`, `mentor`, `employee`). Student routes stay open; `/emp_login` is open; all `/emp_*` CRUD requires admin or manager.

```python
bearer = HTTPBearer()     # reads "Authorization: Bearer <token>" + adds Authorize button

def admin_or_manager(creds = Depends(bearer)):
    try:
        payload = jwt.decode(creds.credentials, SECURITY_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if payload.get("role") not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only admin and manager are allowed")

    return payload
```

Each protected route adds one parameter: `user = Depends(admin_or_manager)`.

- 401 = bad / missing / expired token
- 403 = valid token but wrong role (mentor, employee)
- Role is read from the token (fast), not re-queried from the DB each time
- First admin must be inserted once in pgAdmin (SQL `INSERT INTO employees ...` with a bcrypt-hashed password), since `/emp_create` itself requires an admin to be logged in
- Swagger: click Authorize 🔒 → paste the token (without "Bearer")

---

## 9. Middleware

Runs on every single request (student + employee + login + /docs):

```python
@app.middleware("http")
async def my_middleware(request: Request, call_next):
    print("Request:", request.method, request.url.path)
    response = await call_next(request)
    print("Response:", response.status_code)
    return response
```

- Must be `async def` because of `await call_next(request)` (that's the Python rule: `await` only works inside `async def`)
- CRUD / login / guard functions stay regular `def` — SQLAlchemy's `db.query(...)` is blocking, so plain `def` is correct (FastAPI runs them in a thread pool)

---

## 10. Troubleshooting log

- `uvicorn not recognized` → `unicorn` was installed by mistake: `pip uninstall -y unicorn; pip install "uvicorn[standard]"`
- `Activate.ps1 cannot be loaded` → `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`
- 500 Internal Server Error → read the last line in the VS Code terminal. `column ... does not exist` → run `ALTER TABLE ... ADD COLUMN` in fastapi_db.
- Update "successful" but DB unchanged → the update function didn't assign that field; also re-run the SELECT in pgAdmin (it doesn't auto-refresh).
- Login 404 after hashing → stored password was still plain text or a different password; re-save it through PUT update.
- Every token suddenly "Invalid token" → SECURITY_KEY is random (`secrets.token_hex`) and the server reloaded. Use a fixed string.
- `NameError: admin_or_manager / hash_password is not defined` → the function must be defined ABOVE the routes that use it.
- Swagger lock 🔒 missing on routes → make sure `HTTPBearer()` is used via `Depends(bearer)` inside the guard; without that, Swagger doesn't know the route needs a token.
