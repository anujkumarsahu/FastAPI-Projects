from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean, Date,text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import event

class User(Base):
    __tablename__ = "tbl_users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(name={self.name}, email={self.email})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }

    def __str__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    legal_name = Column(String)
    email = Column(String, nullable=True)
    phone = Column(String)
    established_year = Column(Integer)
    address = Column(String)
    website = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    zip_code = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    IP = Column(String)

    branches = relationship("Branch", back_populates="company")

    def __str__(self):
        return self.name

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String, unique=True, nullable=False, index=True)
    short_name = Column(String, unique=True, nullable=False)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    zip_code = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    IP = Column(String)

    company = relationship("Company", back_populates="branches")
    departments = relationship("Department", back_populates="branch")

    def __str__(self):
        return f'{self.name} [{self.short_name}]'

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    name = Column(String, nullable=False)
    short_name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    IP = Column(String)

    branch = relationship("Branch", back_populates="departments")

    def __str__(self):
        return f'{self.name} [{self.short_name}]'

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    short_name = Column(String, nullable=False, index=True)
    status = Column(String)
    priority = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Float, default=0.0, nullable=False)
    description = Column(String)
    client_name = Column(String)
    client_email = Column(String)
    client_phone = Column(String)
    client_address = Column(String)
    remarks = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    IP = Column(String)

    def __str__(self):
        return f'{self.name} [{self.short_name}]'

class Designation(Base):
    __tablename__ = "designations"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    IP = Column(String)

    def __str__(self):
        return self.name

class EmployeeType(Base):
    __tablename__ = "employee_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    IP = Column(String)

    def __str__(self):
        return self.name

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    min_salary = Column(Float, default=0.0, nullable=False)
    max_salary = Column(Float, default=0.0, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    IP = Column(String)

    def __str__(self):
        return self.name

class DocumentType(Base):
    __tablename__ = "document_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    IP = Column(String)

    def __str__(self):
        return self.name

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    profile_picture = Column(String)
    name = Column(String, nullable=False)
    father_name = Column(String)
    mother_name = Column(String)
    date_of_birth = Column(Date)
    age = Column(Integer)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, unique=True, nullable=False, index=True)
    gender = Column(String)
    marital_status = Column(String)
    blood_group = Column(String)
    category = Column(String)
    religion = Column(String)
    nationality = Column(String)
    adhaar_number = Column(String, unique=True, index=True)
    pan_number = Column(String, unique=True, nullable=True, index=True)
    passport_number = Column(String, unique=True,nullable=True, index=True)
    esic_number = Column(String, unique=True,nullable=True, index=True)
    uan_number = Column(String, unique=True, nullable=True, index=True)
    pf_number = Column(String, unique=True, nullable=True, index=True)
    is_disability = Column(Boolean, default=False)
    disability_type = Column(String, nullable=True)
    disability_certificate_file = Column(String, nullable=True)
    current_address = Column(String)
    current_postal_code = Column(String)
    current_city = Column(String)
    current_state = Column(String)
    current_country = Column(String)
    permanent_postal_code = Column(String)
    permanent_address = Column(String)
    permanent_city = Column(String)
    permanent_state = Column(String)
    permanent_country = Column(String)
    emergency_contact_name = Column(String)
    emergency_contact_relationship = Column(String)
    emergency_contact_phone = Column(String)
    employee_code = Column(String, unique=True, index=True)
    official_email = Column(String, unique=True, nullable=True, index=True)
    date_of_joining = Column(DateTime)
    rejoin_date = Column(DateTime, default=None)
    date_of_leaving = Column(DateTime, default=None)
    reason_of_leaving = Column(String,default=None)
    relieving_certificate_file = Column(String, nullable=True)
    probation_period_months = Column(Integer, default=3)
    confirmation_date = Column(DateTime, default=None)
    notice_period_days = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    IP = Column(String)

    bank_details = relationship("BankDetail", back_populates="employee")
    employee_profiles = relationship(
        "EmployeeProfile",
        back_populates="employee",
        foreign_keys="[EmployeeProfile.employee_id]"
    )

    def __str__(self):
        return self.name

@event.listens_for(Employee, "after_insert")
def generate_employee_code(mapper, connection, target):
    if not target.employee_code and target.id:
        employee_code = f"EMP-{target.id:06d}"
        connection.execute(Employee.__table__.update().
            where(Employee.id == target.id).values(employee_code=employee_code))

class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    designation_id = Column(Integer, ForeignKey("designations.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    employee_type_id = Column(Integer, ForeignKey("employee_types.id"), nullable=False)
    reporting_manager_id = Column(Integer, ForeignKey("employees.id"))
    work_location = Column(String)
    shift_timing = Column(String)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False)
    effective_date = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    IP = Column(String)

    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="employee_profiles")
    designation = relationship("Designation")
    department = relationship("Department")
    branch = relationship("Branch")
    employee_type = relationship("EmployeeType")
    reporting_manager = relationship("Employee", foreign_keys=[reporting_manager_id])
    grade = relationship("Grade")

    def __str__(self):
        return f'Profile of {self.employee.name}'

class BankDetail(Base):
    __tablename__ = "bank_details"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    bank_name = Column(String, nullable=False)
    account_number = Column(String, unique=True, nullable=False, index=True)
    ifsc_code = Column(String, nullable=False)
    branch_name = Column(String, nullable=False)
    account_type = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    IP = Column(String)

    employee = relationship("Employee", back_populates="bank_details")

    def __str__(self):
        return f'Bank Detail of {self.employee.name}'

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    document_type_id = Column(Integer, ForeignKey("document_types.id"), nullable=False)
    document_file = Column(String, nullable=False)
    issue_date = Column(DateTime, default=None)
    expiry_date = Column(DateTime, default=None)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    IP = Column(String)

    employee = relationship("Employee")
    document_type = relationship("DocumentType")

    def __str__(self):
        return f'{self.document_type.name} of {self.employee.name}'

class WorkExperience(Base):
    __tablename__ = "work_experiences"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    company_name = Column(String, nullable=False)
    designation = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    responsibilities = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    IP = Column(String)

    employee = relationship("Employee")

    def __str__(self):
        return f'Work Experience of {self.employee.name} at {self.company_name}'

class Education(Base):
    __tablename__ = "educations"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    institution_name = Column(String, nullable=False)
    degree = Column(String)
    field_of_study = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    grade = Column(String)
    grade_value = Column(Float, default=0.0)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    IP = Column(String)

    employee = relationship("Employee")

    def __str__(self):
        return f'Education of {self.employee.name} at {self.institution_name}'
