from fastapi import FastAPI, Depends, HTTPException, status, Request
from datetime import date, datetime,timedelta
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .models import User, Company, Branch, Department, Project, Employee, Designation, EmployeeType, Grade,DocumentType, Employee, EmployeeProfile, BankDetail, Document, WorkExperience, Education
from .database import SessionLocal, engine, Base
from .auth import hash_password, verify_password, create_access_token, decode_access_token
from typing import Optional

Base.metadata.create_all(bind=engine)
app = FastAPI()
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     token = credentials.credentials
#     payload = decode_access_token(token)
#     if not payload:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
#     return payload.get("sub")

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

@app.post("/register", status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pwd = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "name": new_user.name, "email": new_user.email}

class UserLogin(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": db_user.email}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer","user":db_user}

# @app.get("/users/me")
# def read_users_me(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: Session = Depends(get_db)
# ):
#     token = credentials.credentials
#     payload = decode_access_token(token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     email = payload.get("sub")
#     db_user = db.query(User).filter(User.email == email).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"id": db_user.id, "name": db_user.name, "email": db_user.email}



# @app.get("/protected")
def protected_route(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token or expired token")
    return {"message": "This is a protected route", "user": payload.get("sub")}

############################################### Company CRUD Operations #####################################################
class CompanyBase(BaseModel):
    name: str
    legal_name: str
    email: str
    phone: str
    established_year: int
    address: str
    website: str
    city: str
    state: str
    country: str
    zip_code: str
    is_active: bool

class CompanyCreate(CompanyBase):
    pass

class CompanyRead(CompanyBase):
    id: int
    class Config:
        orm_mode = True

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    legal_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    established_year: Optional[int] = None
    address: Optional[str] = None
    website: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    is_active: Optional[bool] = None
    class Config:
        orm_mode = True

# Routes

@app.get("/companies", response_model=list[CompanyRead])
def read_companies(db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    companies = db.query(Company).filter(Company.is_active == True).all()
    return companies

@app.post("/companies", status_code=201, response_model=CompanyRead)
def create_company(company: CompanyCreate, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@app.get("/companies/{company_id}", response_model=CompanyRead)
def read_company(company_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@app.patch("/companies/{company_id}", response_model=CompanyRead)
def partial_update_company(company_id: int, company: CompanyUpdate, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")

    update_data = company.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_company, key, value)

    db.commit()
    db.refresh(db_company)
    return db_company

@app.put("/companies/{company_id}", response_model=CompanyRead)
def update_company(company_id: int, company: CompanyUpdate, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")

    update_data = company.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_company, key, value)

    db.commit()
    db.refresh(db_company)
    return db_company

# Use DELETE to deactivate (soft delete)
@app.delete("/companies/{company_id}", status_code=204)
def deactivate_company(company_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")

    db_company.is_active = False
    db.commit()
    return "Deactivated Successfully"
############################################### Branch CRUD Operations #####################################################

class readBranch(BaseModel):
    id: int
    company_id: int
    name: str
    short_name: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    country: str
    zip_code: str
    is_active: bool

    class Config:
        orm_mode = True

class createBranch(BaseModel):
    company_id: int
    name: str
    short_name: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    country: str
    zip_code: str
    is_active: bool

class updateBranch(BaseModel):
    company_id: Optional[int] = None
    name: Optional[str] = None
    short_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        orm_mode = True

@app.get("/branches", response_model=list[readBranch])
def read_branches(db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    branches = db.query(Branch).filter(Branch.is_active == True).all()
    return branches

@app.post("/branches", status_code=201, response_model=readBranch)
def create_branch(branch: createBranch, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    existing_branch_name = db.query(Branch).filter(Branch.name == branch.name).first()
    existing_branch_short_name = db.query(Branch).filter(Branch.short_name == branch.short_name).first()
    if existing_branch_name or existing_branch_short_name:
        raise HTTPException(status_code=400, detail="Branch with this name or short name already exists")
    db_branch = Branch(**branch.dict())
    db.add(db_branch)
    db.commit()
    db.refresh(db_branch)
    return db_branch

@app.get("/branches/{branch_id}", response_model=readBranch)
def read_branch(branch_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return db_branch

@app.patch("/branches/{branch_id}", response_model=readBranch)
def partial_update_branch(branch_id: int, branch: updateBranch, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    update_data = branch.dict(exclude_unset=True)

    # Check for duplicate name or short_name (excluding current branch)
    if "name" in update_data:
        existing_branch_name = db.query(Branch).filter(Branch.name == update_data["name"], Branch.id != branch_id).first()
        if existing_branch_name:
            raise HTTPException(status_code=400, detail="Branch with this name already exists")
    if "short_name" in update_data:
        existing_branch_short_name = db.query(Branch).filter(Branch.short_name == update_data["short_name"], Branch.id != branch_id).first()
        if existing_branch_short_name:
            raise HTTPException(status_code=400, detail="Branch with this short name already exists")

    for key, value in update_data.items():
        setattr(db_branch, key, value)

    db.commit()
    db.refresh(db_branch)
    return db_branch

@app.put("/branches/{branch_id}", response_model=readBranch)
def update_branch(branch_id: int, branch: updateBranch, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    update_data = branch.dict(exclude_unset=True)

    # Check for duplicate name or short_name (excluding current branch)
    if "name" in update_data:
        existing_branch_name = db.query(Branch).filter(Branch.name == update_data["name"], Branch.id != branch_id).first()
        if existing_branch_name:
            raise HTTPException(status_code=400, detail="Branch with this name already exists")
    if "short_name" in update_data:
        existing_branch_short_name = db.query(Branch).filter(Branch.short_name == update_data["short_name"], Branch.id != branch_id).first()
        if existing_branch_short_name:
            raise HTTPException(status_code=400, detail="Branch with this short name already exists")

    for key, value in update_data.items():
        setattr(db_branch, key, value)

    db.commit()
    db.refresh(db_branch)
    return db_branch
# Use DELETE to deactivate (soft delete)
@app.delete("/branches/{branch_id}", status_code=204)
def deactivate_branch(branch_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    db_branch.is_active = False
    db.commit()
    return "Deactivated Successfully"
############################################### Department CRUD Operations #####################################################

class readDepartment(BaseModel):
    id: int
    branch_id: int
    name: str
    short_name: str
    description: str
    is_active: bool

    class Config:
        orm_mode = True
class createDepartment(BaseModel):
    branch_id: int
    name: str
    short_name: str
    description: str
    is_active: bool

class updateDepartment(BaseModel):
    branch_id: Optional[int] = None
    name: Optional[str] = None
    short_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        orm_mode = True

@app.get("/departments", response_model=list[readDepartment])
def read_departments(db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    departments = db.query(Department).filter(Department.is_active == True).all()
    return departments

@app.post("/departments", status_code=201, response_model=readDepartment)
def create_department(department: createDepartment, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    existing_department_name = db.query(Department).filter(Department.branch_id == department.branch_id, Department.name == department.name).first()
    existing_department_short_name = db.query(Department).filter(Department.branch_id == department.branch_id, Department.short_name == department.short_name).first()
    if existing_department_name or existing_department_short_name:
        raise HTTPException(status_code=400, detail="Department with this name or short name already exists")
    db_department = Department(**department.dict())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

@app.get("/departments/{department_id}", response_model=readDepartment)
def read_department(department_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_department = db.query(Department).filter(Department.id == department_id).first()
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")
    return db_department


@app.patch("/departments/{department_id}", response_model=readDepartment)
def partial_update_department(department_id: int, department: updateDepartment, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_department = db.query(Department).filter(Department.id == department_id).first()
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")

    update_data = department.dict(exclude_unset=True)

    # Check for duplicate name or short_name (excluding current department)
    if "name" in update_data:
        existing_department_name = db.query(Department).filter(Department.name == update_data["name"], Department.id != department_id).first()
        if existing_department_name:
            raise HTTPException(status_code=400, detail="Department with this name already exists")
    if "short_name" in update_data:
        existing_department_short_name = db.query(Department).filter(Department.short_name == update_data["short_name"], Department.id != department_id).first()
        if existing_department_short_name:
            raise HTTPException(status_code=400, detail="Department with this short name already exists")

    for key, value in update_data.items():
        setattr(db_department, key, value)

    db.commit()
    db.refresh(db_department)
    return db_department

@app.put("/departments/{department_id}", response_model=readDepartment)
def update_department(department_id: int, department: updateDepartment, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_department = db.query(Department).filter(Department.id == department_id).first()
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")

    update_data = department.dict(exclude_unset=True)

    # Check for duplicate name or short_name (excluding current department)
    if "name" in update_data:
        existing_department_name = db.query(Department).filter(Department.name == update_data["name"], Department.id != department_id).first()
        if existing_department_name:
            raise HTTPException(status_code=400, detail="Department with this name already exists")
    if "short_name" in update_data:
        existing_department_short_name = db.query(Department).filter(Department.short_name == update_data["short_name"], Department.id != department_id).first()
        if existing_department_short_name:
            raise HTTPException(status_code=400, detail="Department with this short name already exists")

    for key, value in update_data.items():
        setattr(db_department, key, value)

    db.commit()
    db.refresh(db_department)
    return db_department

# Use DELETE to deactivate (soft delete)
@app.delete("/departments/{department_id}", status_code=204)
def deactivate_department(department_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_department = db.query(Department).filter(Department.id == department_id).first()
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")

    db_department.is_active = False
    db.commit()
    return "Deactivated Successfully"

############################################### Project CRUD Operations #####################################################

class readProject(BaseModel):
    id: int
    name: str
    short_name: str
    status: str  # e.g., Planned, In Progress, Completed
    priority: str  # e.g., Low, Medium, High
    start_date: date
    end_date: date
    budget: float
    description: str
    client_name: str
    client_email: str
    client_phone: str
    client_address: str
    remarks: str
    is_active: bool = True  # True for active, False for inactive

    class Config:
        orm_mode = True

class createProject(BaseModel):
    name: str
    short_name: str
    status: str  # e.g., Planned, In Progress, Completed
    priority: str  # e.g., Low, Medium, High
    start_date: date
    end_date: date
    budget: float
    description: str
    client_name: str
    client_email: str
    client_phone: str
    client_address: str
    remarks: str
    is_active: bool = True  # True for active, False for inactive
class updateProject(BaseModel):
    name: Optional[str]= None
    short_name: Optional[str]= None
    status: Optional[str]= None  # e.g., Planned, In Progress, Completed
    priority: Optional[str]= None  # e.g., Low, Medium, High
    start_date: Optional[date]= None
    end_date: Optional[date]= None
    budget: Optional[float]= None
    description: Optional[str]= None
    client_name: Optional[str]= None
    client_email: Optional[str]= None
    client_phone: Optional[str]= None
    client_address: Optional[str]= None
    remarks: Optional[str]= None
    is_active: Optional[bool]= None
    
    class Config:
        orm_mode = True

@app.get("/projects", response_model=list[readProject])
def read_projects(db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    projects = db.query(Project).filter(Project.is_active == True).all()
    return projects

@app.post("/projects", status_code=201, response_model=readProject)
def create_project(project: createProject, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    existing_project_name = db.query(Project).filter(Project.name == project.name).first()
    existing_project_short_name = db.query(Project).filter(Project.short_name == project.short_name).first()
    
    if existing_project_name or existing_project_short_name:
        raise HTTPException(status_code=400, detail="Project with this name or short name already exists")
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/{project_id}", response_model=readProject)
def read_project(project_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.patch("/projects/{project_id}", response_model=readProject)
def partial_update_project(project_id: int, project: updateProject, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project.dict(exclude_unset=True)

    # Check for duplicate name or short_name (excluding current project)
    if "name" in update_data:
        existing_project_name = db.query(Project).filter(Project.name == update_data["name"], Project.id != project_id).first()
        if existing_project_name:
            raise HTTPException(status_code=400, detail="Project with this name already exists")
    if "short_name" in update_data:
        existing_project_short_name = db.query(Project).filter(Project.short_name == update_data["short_name"], Project.id != project_id).first()
        if existing_project_short_name:
            raise HTTPException(status_code=400, detail="Project with this short name already exists")

    for key, value in update_data.items():
        setattr(db_project, key, value)

    db.commit()
    db.refresh(db_project)
    return db_project

@app.put("/projects/{project_id}", response_model=readProject)
def update_project(project_id: int, project: updateProject, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project.dict(exclude_unset=True)

    # Check for duplicate name or short_name (excluding current project)
    if "name" in update_data:
        existing_project_name = db.query(Project).filter(Project.name == update_data["name"], Project.id != project_id).first()
        if existing_project_name:
            raise HTTPException(status_code=400, detail="Project with this name already exists")
    if "short_name" in update_data:
        existing_project_short_name = db.query(Project).filter(Project.short_name == update_data["short_name"], Project.id != project_id).first()
        if existing_project_short_name:
            raise HTTPException(status_code=400, detail="Project with this short name already exists")

    for key, value in update_data.items():
        setattr(db_project, key, value)

    db.commit()
    db.refresh(db_project)
    return db_project

# Use DELETE to deactivate (soft delete)
@app.delete("/projects/{project_id}", status_code=204)
def deactivate_project(project_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_project.is_active = False
    db.commit()
    return "Deactivated Successfully"

######################################## Employee of CRUD Operations #####################################################
class readEmployeeType(BaseModel):
    id: int
    name: str
    description: str
    is_active: bool

    class Config:
        orm_mode = True
class createEmployeeType(BaseModel):
    name : str
    description : str
    is_active : bool

class updateEmployeeType(BaseModel):
    name : Optional[str] = None
    description : Optional[str] = None
    is_active : Optional[bool] = None

    class Config:
        orm_mode = True
@app.get("/employee_types", response_model=list[readEmployeeType])
def read_employee_types(db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    employee_types = db.query(EmployeeType).filter(EmployeeType.is_active == True).all()
    return employee_types

@app.post("/employee_types", status_code=201, response_model=readEmployeeType)
def create_employee_type(employee_type: createEmployeeType, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    existing_employee_type = db.query(EmployeeType).filter(EmployeeType.name == employee_type.name).first()
    if existing_employee_type:
        raise HTTPException(status_code=400, detail="Employee Type with this name already exists")
    db_employee_type = EmployeeType(**employee_type.dict())
    db.add(db_employee_type)
    db.commit()
    db.refresh(db_employee_type)
    return db_employee_type

@app.get("/employee_types/{employee_type_id}", response_model=readEmployeeType)
def read_employee_type(employee_type_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_employee_type = db.query(EmployeeType).filter(EmployeeType.id == employee_type_id).first()
    if not db_employee_type:
        raise HTTPException(status_code=404, detail="Employee Type not found")
    return db_employee_type

@app.patch("/employee_types/{employee_type_id}", response_model=readEmployeeType)
def partial_update_employee_type(employee_type_id: int, employee_type: updateEmployeeType, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_employee_type = db.query(EmployeeType).filter(EmployeeType.id == employee_type_id).first()
    if not db_employee_type:
        raise HTTPException(status_code=404, detail="Employee Type not found")

    update_data = employee_type.dict(exclude_unset=True)

    # Check for duplicate name (excluding current employee type)
    if "name" in update_data:
        existing_employee_type = db.query(EmployeeType).filter(EmployeeType.name == update_data["name"], EmployeeType.id != employee_type_id).first()
        if existing_employee_type:
            raise HTTPException(status_code=400, detail="Employee Type with this name already exists")

    for key, value in update_data.items():
        setattr(db_employee_type, key, value)

    db.commit()
    db.refresh(db_employee_type)
    return db_employee_type
@app.put("/employee_types/{employee_type_id}", response_model=readEmployeeType)
def update_employee_type(employee_type_id: int, employee_type: updateEmployeeType, db:Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_employee_type = db.query(EmployeeType).filter(EmployeeType.id == employee_type_id).first()
    if not db_employee_type:
        raise HTTPException(status_code=404, detail="Employee Type not found")

    update_data = employee_type.dict(exclude_unset=True)

    # Check for duplicate name (excluding current employee type)
    if "name" in update_data:
        existing_employee_type = db.query(EmployeeType).filter(EmployeeType.name == update_data["name"], EmployeeType.id != employee_type_id).first()
        if existing_employee_type:
            raise HTTPException(status_code=400, detail="Employee Type with this name already exists")

    for key, value in update_data.items():
        setattr(db_employee_type, key, value)

    db.commit()
    db.refresh(db_employee_type)
    return db_employee_type
# Use DELETE to deactivate (soft delete)
@app.delete("/employee_types/{employee_type_id}", status_code=204)
def deactivate_employee_type(employee_type_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_employee_type = db.query(EmployeeType).filter(EmployeeType.id == employee_type_id).first()
    if not db_employee_type:
        raise HTTPException(status_code=404, detail="Employee Type not found")
    db_employee_type.is_active = False
    db.commit()
    return {"detail": "Employee Type deactivated"}

class readGrade(BaseModel):
    id: int
    name: str
    min_salary: float
    max_salary: float
    description: str
    is_active: bool

    class Config:
        orm_mode = True
class createGrade(BaseModel):
    name : str
    min_salary : float
    max_salary : float
    description : str
    is_active : bool
class updateGrade(BaseModel):
    name : Optional[str] = None
    min_salary : Optional[float] = None
    max_salary : Optional[float] = None
    description : Optional[str] = None
    is_active : Optional[bool] = None

    class Config:
        orm_mode = True
@app.get("/grades", response_model=list[readGrade])
def read_grades(db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    grades = db.query(Grade).filter(Grade.is_active == True).all()
    return grades

@app.post("/grades", status_code=201, response_model=readGrade)
def create_grade(grade: createGrade, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    existing_grade = db.query(Grade).filter(Grade.name == grade.name).first()
    if existing_grade:
        raise HTTPException(status_code=400, detail="Grade with this name already exists")
    db_grade = Grade(**grade.dict())
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return db_grade

@app.get("/grades/{grade_id}", response_model=readGrade)
def read_grade(grade_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not db_grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    return db_grade
@app.patch("/grades/{grade_id}", response_model=readGrade)
def partial_update_grade(grade_id: int, grade: updateGrade, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not db_grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    update_data = grade.dict(exclude_unset=True)

    # Check for duplicate name (excluding current grade)
    if "name" in update_data:
        existing_grade = db.query(Grade).filter(Grade.name == update_data["name"], Grade.id != grade_id).first()
        if existing_grade:
            raise HTTPException(status_code=400, detail="Grade with this name already exists")

    for key, value in update_data.items():
        setattr(db_grade, key, value)

    db.commit()
    db.refresh(db_grade)
    return db_grade

@app.put("/grades/{grade_id}", response_model=readGrade)
def update_grade(grade_id: int, grade: updateGrade, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not db_grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    update_data = grade.dict(exclude_unset=True)

    # Check for duplicate name (excluding current grade)
    if "name" in update_data:
        existing_grade = db.query(Grade).filter(Grade.name == update_data["name"], Grade.id != grade_id).first()
        if existing_grade:
            raise HTTPException(status_code=400, detail="Grade with this name already exists")

    for key, value in update_data.items():
        setattr(db_grade, key, value)

    db.commit()
    db.refresh(db_grade)
    return db_grade

# Use DELETE to deactivate (soft delete)
@app.delete("/grades/{grade_id}", status_code=204)
def deactivate_grade(grade_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not db_grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    db_grade.is_active = False
    db.commit()
    return {"detail": "Grade deactivated"}


class readDocumentType(BaseModel):
    id: int
    name: str
    description: str
    is_active: bool

    class Config:
        orm_mode = True
class createDocumentType(BaseModel):
    name : str
    description : str
    is_active : bool

class updateDocumentType(BaseModel):
    name : Optional[str]= None
    description : Optional[str]= None
    is_active : Optional[bool]= None
    
    class Config:
        orm_mode = True

@app.get("/document_types", response_model=list[readDocumentType])
def read_document_types(db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    document_types = db.query(DocumentType).filter(DocumentType.is_active == True).all()
    return document_types

@app.post("/document_types", status_code=201, response_model=readDocumentType)
def create_document_type(document_type: createDocumentType, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    existing_document_type = db.query(DocumentType).filter(DocumentType.name == document_type.name).first()
    if existing_document_type:
        raise HTTPException(status_code=400, detail="Document Type with this name already exists")
    db_document_type = DocumentType(**document_type.dict())
    db.add(db_document_type)
    db.commit()
    db.refresh(db_document_type)
    return db_document_type

@app.get("/document_types/{document_type_id}", response_model=readDocumentType)
def read_document_type(document_type_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_document_type = db.query(DocumentType).filter(DocumentType.id == document_type_id).first()
    if not db_document_type:
        raise HTTPException(status_code=404, detail="Document Type not found")
    return db_document_type

@app.patch("/document_types/{document_type_id}", response_model=readDocumentType)
def partial_update_document_type(document_type_id: int, document_type: updateDocumentType, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_document_type = db.query(DocumentType).filter(DocumentType.id == document_type_id).first()
    if not db_document_type:
        raise HTTPException(status_code=404, detail="Document Type not found")

    update_data = document_type.dict(exclude_unset=True)

    # Check for duplicate name (excluding current document type)
    if "name" in update_data:
        existing_document_type = db.query(DocumentType).filter(DocumentType.name == update_data["name"], DocumentType.id != document_type_id).first()
        if existing_document_type:
            raise HTTPException(status_code=400, detail="Document Type with this name already exists")

    for key, value in update_data.items():
        setattr(db_document_type, key, value)

    db.commit()
    db.refresh(db_document_type)
    return db_document_type

@app.put("/document_types/{document_type_id}", response_model=readDocumentType)
def update_document_type(document_type_id: int, document_type: updateDocumentType, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_document_type = db.query(DocumentType).filter(DocumentType.id == document_type_id).first()
    if not db_document_type:
        raise HTTPException(status_code=404, detail="Document Type not found")

    update_data = document_type.dict(exclude_unset=True)
    # Check for duplicate name (excluding current document type)
    if "name" in update_data:
        existing_document_type = db.query(DocumentType).filter(DocumentType.name == update_data["name"], DocumentType.id != document_type_id).first()
        if existing_document_type:
            raise HTTPException(status_code=400, detail="Document Type with this name already exists")

    for key, value in update_data.items():
        setattr(db_document_type, key, value)

    db.commit()
    db.refresh(db_document_type)
    return db_document_type

# Use DELETE to deactivate (soft delete)
@app.delete("/document_types/{document_type_id}", status_code=204)
def delete_document_type(document_type_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_document_type = db.query(DocumentType).filter(DocumentType.id == document_type_id).first()
    if not db_document_type:
        raise HTTPException(status_code=404, detail="Document Type not found")
    db_document_type.is_active = False
    db.commit()
    return {"detail": "Document Type deactivated"}

class readEmployee(BaseModel):
    id : int
    profile_picture : str = None
    name : str = None
    father_name : str = None
    mother_name : str = None
    date_of_birth : date = None
    age : int = None
    email : str = None
    phone : str = None
    gender : str = None # e.g., Male, Female, Other, Prefer not to say
    marital_status : str = None # e.g., Single, Married, Divorced, Widowed, Separated
    blood_group : str = None # e.g., A+, A-, B+, B-, AB+, AB-, O+, O-
    category : str = None # e.g., General, OBC, SC, ST, EWS
    religion : str = None # e.g., Hinduism, Islam, Christianity, Sikhism, Buddhism, Jainism, Other, Prefer not to say
    nationality : str = None # e.g., Indian, American, British, Canadian, Australian, Other
    adhaar_number : str = None
    pan_number : str = None
    passport_number : str = None
    esic_number : str = None
    uan_number : str = None
    pf_number : str = None
    is_disability : bool = None
    disability_type : str = None # e.g., Visual, Hearing, Speech, Physical, Intellectual, Mental, Multiple
    disability_certificate_file : str = None # URL or file path to the disability certificate

    current_address : str
    current_postal_code : str
    current_city : str
    current_state : str
    current_country : str

    permanent_postal_code : str
    permanent_address : str
    permanent_city : str
    permanent_state : str
    permanent_country : str

    emergency_contact_name : str
    emergency_contact_relationship : str
    emergency_contact_phone : str

    employee_code : str = None
    official_email : str = None
    date_of_joining : datetime = None
    rejoin_date : datetime = None
    date_of_leaving : datetime = None
    reason_of_leaving : str = None
    relieving_certificate_file : str = None # URL or file path to the relieving certificate
    probation_period_months : int = 3
    confirmation_date : datetime = None
    notice_period_days : int = 30

    class Config:
        orm_mode = True
        
class createEmployee(BaseModel):
    profile_picture : str = None
    name : str
    father_name : str
    mother_name : str
    date_of_birth : date
    age : int = None
    email : str 
    phone : str 
    gender : str
    marital_status : str 
    blood_group : str = None
    category : str = None
    religion : str = None
    nationality : str = None
    adhaar_number : str = None
    pan_number : str = None
    passport_number : str = None
    esic_number : str = None
    uan_number : str = None
    pf_number : str = None
    is_disability : bool = False
    disability_type : str = None
    disability_certificate_file : str = None
    current_address : str = None
    current_postal_code : str = None
    current_city : str = None
    current_state : str = None
    current_country : str = None
    permanent_postal_code : str = None
    permanent_address : str = None
    permanent_city : str = None
    permanent_state : str = None
    permanent_country : str = None
    emergency_contact_name : str = None
    emergency_contact_relationship : str = None
    emergency_contact_phone : str = None
    employee_code : str = None
    official_email : str = None
    date_of_joining : datetime = None
    rejoin_date : datetime = None
    date_of_leaving : datetime = None
    reason_of_leaving : str = None
    relieving_certificate_file : str = None
    probation_period_months : int = 3
    confirmation_date : datetime = None
    notice_period_days : int = 30

class updateEmployee(BaseModel):
    profile_picture : Optional[str] = None
    name : Optional[str] = None
    father_name : Optional[str] = None
    mother_name : Optional[str] = None
    date_of_birth : Optional[date] = None
    age : Optional[int] = None
    email : Optional[str] = None
    phone : Optional[str] = None
    gender : Optional[str] = None
    marital_status : Optional[str] = None
    blood_group : Optional[str] = None
    category : Optional[str] = None
    religion : Optional[str] = None
    nationality : Optional[str] = None
    adhaar_number : Optional[str] = None
    pan_number : Optional[str] = None
    passport_number : Optional[str] = None
    esic_number : Optional[str] = None
    uan_number : Optional[str] = None
    pf_number : Optional[str] = None
    is_disability : Optional[bool] = None
    disability_type : Optional[str] = None
    disability_certificate_file : Optional[str] = None
    current_address : Optional[str] = None
    current_postal_code : Optional[str] = None
    current_city : Optional[str] = None
    current_state : Optional[str] = None
    current_country : Optional[str] = None
    permanent_postal_code : Optional[str] = None
    permanent_address : Optional[str] = None
    permanent_city : Optional[str] = None
    permanent_state : Optional[str] = None
    permanent_country : Optional[str] = None
    emergency_contact_name : Optional[str] = None
    emergency_contact_relationship : Optional[str] = None
    emergency_contact_phone : Optional[str] = None
    employee_code : Optional[str] = None
    official_email : Optional[str] = None
    date_of_joining : Optional[datetime] = None
    rejoin_date : Optional[datetime] = None
    date_of_leaving : Optional[datetime] = None
    reason_of_leaving : Optional[str] = None
    relieving_certificate_file : Optional[str] = None
    probation_period_months : Optional[int] = 3
    confirmation_date : Optional[datetime] = None
    notice_period_days : Optional[int] = 30

    class Config:
        orm_mode = True

@app.get("/employees", response_model=list[readEmployee])
def read_employees(db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    employees = db.query(Employee).filter(Employee.is_active == True).all()
    return employees

@app.post("/employees", status_code=201, response_model=readEmployee)
def create_employee(employee: createEmployee, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    # Check for duplicate email, phone
    if employee.email:
        existing_employee_email = db.query(Employee).filter(Employee.email == employee.email).first()
        if existing_employee_email:
            raise HTTPException(status_code=400, detail="Employee with this email already exists")
    if employee.phone:
        existing_employee_phone = db.query(Employee).filter(Employee.phone == employee.phone).first()
        if existing_employee_phone:
            raise HTTPException(status_code=400, detail="Employee with this phone already exists")
    
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.get("/employees/{employee_id}", response_model=readEmployee)
def read_employee(employee_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@app.patch("/employees/{employee_id}", response_model=readEmployee)
def partial_update_employee(employee_id: int, employee: updateEmployee, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = employee.model_dump(exclude_unset=True)

    # Check for duplicate email, phone or employee code (excluding current employee)
    if "email" in update_data:
        existing_employee_email = db.query(Employee).filter(Employee.email == update_data["email"], Employee.id != employee_id).first()
        if existing_employee_email:
            raise HTTPException(status_code=400, detail="Employee with this email already exists")
    if "phone" in update_data:
        existing_employee_phone = db.query(Employee).filter(Employee.phone == update_data["phone"], Employee.id != employee_id).first()
        if existing_employee_phone:
            raise HTTPException(status_code=400, detail="Employee with this phone already exists")
    if "employee_code" in update_data:
        existing_employee_code = db.query(Employee).filter(Employee.employee_code == update_data["employee_code"], Employee.id != employee_id).first()
        if existing_employee_code:
            raise HTTPException(status_code=400, detail="Employee with this employee code already exists")

    for key, value in update_data.items():
        setattr(db_employee, key, value)

    db.commit()
    db.refresh(db_employee)
    return db_employee


@app.put("/employees/{employee_id}", response_model=readEmployee)
def update_employee(employee_id: int, employee: updateEmployee, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = employee.model_dump(exclude_unset=True)

    # Check for duplicate email, phone or employee code (excluding current employee)
    if "email" in update_data:
        existing_employee_email = db.query(Employee).filter(Employee.email == update_data["email"], Employee.id != employee_id).first()
        if existing_employee_email:
            raise HTTPException(status_code=400, detail="Employee with this email already exists")
    if "phone" in update_data:
        existing_employee_phone = db.query(Employee).filter(Employee.phone == update_data["phone"], Employee.id != employee_id).first()
        if existing_employee_phone:
            raise HTTPException(status_code=400, detail="Employee with this phone already exists")
    if "employee_code" in update_data:
        existing_employee_code = db.query(Employee).filter(Employee.employee_code == update_data["employee_code"], Employee.id != employee_id).first()
        if existing_employee_code:
            raise HTTPException(status_code=400, detail="Employee with this employee code already exists")

    for key, value in update_data.items():
        setattr(db_employee, key, value)

    db.commit()
    db.refresh(db_employee)
    return db_employee

# Use DELETE to deactivate (soft delete)
@app.delete("/employees/{employee_id}", status_code=204)
def deactivate_employee(employee_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db_employee.is_active = False
    db.commit()
    return {"detail": "Employee deactivated"}

######################################## Employee Profile CRUD Operations #####################################################

class BaseEmployeeProfile(BaseModel):
    employee_id: int
    employee_type_id: int
    branch_id: int
    department_id: int
    designation_id: int
    grade_id: int
    reporting_manager_id: int
    work_location: str
    shift_timing: str
    effective_date: date

class readEmployeeProfile(BaseEmployeeProfile):
    id: int
    class Config:
        orm_mode = True

class createEmployeeProfile(BaseEmployeeProfile):
    class Config:
        orm_mode = True

class updateEmployeeProfile(BaseModel):
    employee_id: Optional[int] = None
    employee_type_id: Optional[int] = None
    branch_id: Optional[int] = None
    department_id: Optional[int] = None
    designation_id: Optional[int] = None
    grade_id: Optional[int] = None
    reporting_manager_id: Optional[int] = None
    work_location: Optional[str] = None
    shift_timing: Optional[str] = None
    effective_date: Optional[date] = None

    class Config:
        orm_mode = True

@app.get("/employeeprofile", response_model=list[readEmployeeProfile])
def read_employee_profile(db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    employee_profiles = db.query(EmployeeProfile).filter(EmployeeProfile.is_active == True).all()
    return employee_profiles

@app.post("/employeeprofile", status_code=201, response_model=readEmployeeProfile)
def create_employeeprofile(employee_profile: createEmployeeProfile, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    # Check for duplicate profile with same data
    existing_employee_profile = db.query(EmployeeProfile).filter(
        EmployeeProfile.employee_id == employee_profile.employee_id,
        EmployeeProfile.employee_type_id == employee_profile.employee_type_id,
        EmployeeProfile.branch_id == employee_profile.branch_id,
        EmployeeProfile.department_id == employee_profile.department_id,
        EmployeeProfile.designation_id == employee_profile.designation_id,
        EmployeeProfile.grade_id == employee_profile.grade_id,
        EmployeeProfile.reporting_manager_id == employee_profile.reporting_manager_id,
        EmployeeProfile.work_location == employee_profile.work_location,
        EmployeeProfile.shift_timing == employee_profile.shift_timing,
        EmployeeProfile.is_active == True
    ).first()
    if existing_employee_profile:
        raise HTTPException(status_code=400, detail="Employee profile with same data already exists.")

    # Deactivate previous active profile for this employee (if any)
    previous_active_profile = db.query(EmployeeProfile).filter(
        EmployeeProfile.employee_id == employee_profile.employee_id,
        EmployeeProfile.is_active == True
    ).first()
    if previous_active_profile:
        previous_active_profile.is_active = False
        db.commit()

    db_employee_profile = EmployeeProfile(**employee_profile.model_dump())
    db.add(db_employee_profile)
    db.commit()
    db.refresh(db_employee_profile)
    return db_employee_profile

@app.get("/employeeprofile/{profile_id}", response_model=readEmployeeProfile)
def get_employee_profile(profile_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_profile = db.query(EmployeeProfile).filter(EmployeeProfile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return db_profile

@app.patch("/employeeprofile/{profile_id}", response_model=readEmployeeProfile)
def update_employee_profile_partial(profile_id: int, profile: updateEmployeeProfile, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_profile = db.query(EmployeeProfile).filter(EmployeeProfile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    update_data = profile.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_profile, key, value)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@app.delete("/employeeprofile/{profile_id}", status_code=204)
def deactivate_employee_profile(profile_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_profile = db.query(EmployeeProfile).filter(EmployeeProfile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    db_profile.is_active = False
    db.commit()
    return {"detail": "Employee profile deactivated"}

########## employee bank detail 16-09-2025 ##########

class baseBankDetail(BaseModel):
    employee_id :int
    bank_name:str
    account_number:str
    ifsc_code:str
    branch_name:str
    account_type: str
    is_primary : bool
    
class readBankDetail(baseBankDetail):
    id:int
    
    class Config:
        orm_mode =True
class createBankDetail(baseBankDetail):
    pass

    class Config:
        orm_mode = True

class updateBankDetail(BaseModel):
    employee_id: Optional[int]=None
    bank_name:Optional[str] =None
    account_number: Optional[str]=None
    ifsc_code: Optional[str] = None
    branch_name: Optional[str]=None
    account_type :Optional[str]= None
    is_primary:Optional[bool] = None
    
    class Config:
        orm_mode =True

@app.get("/employeebankdetails", response_model=list[readBankDetail])
def read_employee_bank_details(db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_bank_details = db.query(BankDetail).filter(BankDetail.is_active == True).order_by(BankDetail.account_type.desc()).all()
    return db_bank_details

@app.get("/employeebankdetail/{bankdetail_id}", response_model=readBankDetail)
def read_employee_bank_details(bankdetail_id: int, db: Session = Depends(get_db), user_email: str = Depends(protected_route)):
    db_bank_details = db.query(BankDetail).filter(BankDetail.is_active == True, BankDetail.id == bankdetail_id).first()
    return db_bank_details
            
    
    
@app.post("/employeebankdetail", status_code=201, response_model= readBankDetail)
def create_employee_bank_detail(bank_detail : createBankDetail, db:Session=Depends(get_db), user_email:str=Depends(protected_route)):
    ## check duplicate account
    existing_bank = db.query(BankDetail).filter(BankDetail.account_number == bank_detail.account_number).first()
    if existing_bank:
       raise HTTPException(status_code=400, detail=f"Account number ({bank_detail.account_number}) already exists.") 
   
    db_bank_detail = BankDetail(**bank_detail.model_dump())
    db.add(db_bank_detail)
    db.commit()
    db.refresh(db_bank_detail)
    return db_bank_detail


@app.patch("/employeebankdetail/{bankdetail_id}", response_model=readBankDetail)
def partial_update_employee_bank_detail(
    bankdetail_id: int,
    bank_detail: updateBankDetail,
    db: Session = Depends(get_db),
    user_email: str = Depends(protected_route)
):
    db_bank_detail = db.query(BankDetail).filter(BankDetail.id == bankdetail_id).first()
    if not db_bank_detail:
        raise HTTPException(status_code=404, detail="Bank Detail not Found.")
    update_bank_detail = bank_detail.model_dump(exclude_unset=True)
    for key, value in update_bank_detail.items():
        setattr(db_bank_detail, key, value)
    db.commit()
    db.refresh(db_bank_detail)
    return db_bank_detail

@app.delete("/employeebankdetail/{bankdetail_id}",status_code=204)
def deactivate_bank_detail(bankdetail_id : int, db:Session=Depends(get_db), user_emil:str = Depends(protected_route) ):
    db_bank_detail = db.query(BankDetail).filter(BankDetail.is_active == True, BankDetail.id == bankdetail_id).first()
    if not db_bank_detail:
        raise HTTPException(status_code=404, detail=f"Bank Detail not Found.")
    db_bank_detail.is_active = False
    db.commit()
    db.refresh(db_bank_detail)
    return None

######################## employee Document detail #################

class baseDocument(BaseModel):
    employee_id : int
    document_type_id : int
    document_file : str
    issue_date : date
    expiry_date: date
    is_verified: bool
    
class readDocument(baseDocument):
    id:int

    class Config:
        orm_mode = True
class createDocument(baseDocument):
    pass

    class Config:
        orm_mode = True

class updateDocument(BaseModel):
    employee_id : Optional[int]= None
    document_type_id : Optional[int] = None
    document_file : Optional[str] =None
    issue_date : Optional[date] = None
    expiry_date: Optional[date] = None
    is_verified : Optional[bool] =None
    
    class Config:
        orm_mode= True
        
@app.get("/employeedocuments", response_model=list[readDocument])
def employee_documents(db:Session = Depends(get_db), user_email:str =Depends(protected_route)):
    db_document = db.query(Document).filter(Document.is_active == True).order_by(Document.created_at.desc())
    return db_document

@app.get("/employeedocument/{document_id}", response_model= readDocument)
def employee_document(document_id:int, db: Session=Depends(get_db), user_email:str = Depends(protected_route)):
    db_document = db.query(Document).filter(Document.is_active == True, Document.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404,detail= "Document Not Found.")
    return db_document

@app.post("/employeedocument",status_code=201, response_model= readDocument)
def create_employee_document(document: createDocument, db:Session=Depends(get_db), user_email :str = Depends(protected_route)):
    db_document = Document(**document.model_dump())
    db.add(db_document)
    db.commit
    db.refresh(db_document)
    return db_document

@app.patch("/employeedocument/{document_id}", response_model= readDocument)
def partial_update_employee_document(document_id:int , document: updateDocument, db:Session=Depends(get_db), user_email:str = Depends(protected_route)):
    db_document = db.query(Document).filter(Document.is_active == True, Document.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code= 404, detail= "Document not Found.")
    updated_document = document.model_dump(exclude_unset=True)
    for key,value in updated_document:
        setattr(db_document,key,value)
    db.commit()
    db.refresh(db_document)
    return db_document

@app.delete("/employeedocument/{document_id}", status_code=204)
def deactivate_employee_document(document_id:int, db:Session=Depends(get_db),user_email:str = Depends(protected_route)):
    db_document = db.query(Document).filter(Document.is_active == True, Document.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document Not Found.")
    db_document.is_active == False
    db.commit
    db.refresh(db_document)
    return None
#######################  WorkExperience ####################

        
    
    
    
    