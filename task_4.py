from fastapi import FastAPI, HTTPException, Path, Query, Body
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict
from uuid import uuid4, UUID
from datetime import datetime
import json
import threading
import os

app = FastAPI()
DATA_FILE = "students.json"
lock = threading.Lock()

class StudentBase(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    age: int = Field(...)
    department: Optional[str] = None
    CGPA: int = Field(...)

    @validator("name")
    def name_min_length(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("name must be at least 2 characters")
        return v

    @validator("age")
    def age_range(cls, v):
        if not (10 <= v <= 100):
            raise ValueError("age must be between 10 and 100")
        return v

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    department: Optional[str] = None
    CGPA: Optional[int] = None

    @validator("name")
    def name_min_length(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError("name must be at least 2 characters")
        return v

    @validator("age")
    def age_range(cls, v):
        if v is not None and not (10 <= v <= 100):
            raise ValueError("age must be between 10 and 100")
        return v

class Student(StudentBase):
    id: UUID
    created_at: str

def _read_data() -> List[Dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with lock:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
            except:
                return []

def _write_data(data: List[Dict]):
    with lock:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, default=str, indent=2)

@app.post("/students", response_model=Student, status_code=201)
def create_student(student: StudentCreate = Body(...)):
    data = _read_data()
    if any(s["email"].lower() == student.email.lower() for s in data):
        raise HTTPException(status_code=400, detail="email already exists")
    new_student = {
        "id": str(uuid4()),
        "name": student.name.strip(),
        "email": student.email,
        "age": student.age,
        "department": student.department,
        "created_at": datetime.utcnow().isoformat(),
        "CGPA": student.CGPA
    }
    data.append(new_student)
    _write_data(data)
    return new_student

@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: UUID = Path(...)):
    data = _read_data()
    for s in data:
        if s["id"] == str(student_id):
            return s
    raise HTTPException(status_code=404, detail="student not found")

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: UUID = Path(...), update: StudentUpdate = Body(...)):
    data = _read_data()
    for i, s in enumerate(data):
        if s["id"] == str(student_id):
            if update.email:
                if any(other["email"].lower() == update.email.lower() and other["id"] != s["id"] for other in data):
                    raise HTTPException(status_code=400, detail="email already exists")
                s["email"] = update.email
            if update.name is not None:
                if len(update.name.strip()) < 2:
                    raise HTTPException(status_code=400, detail="name must be at least 2 characters")
                s["name"] = update.name.strip()
            if update.age is not None:
                if not (10 <= update.age <= 100):
                    raise HTTPException(status_code=400, detail="age must be between 10 and 100")
                s["age"] = update.age
            if update.department is not None:
                s["department"] = update.department
            if update.CGPA is not None:
                s["CGPA"] = update.CGPA
            data[i] = s
            _write_data(data)
            return s
    raise HTTPException(status_code=404, detail="student not found")

@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: UUID = Path(...)):
    data = _read_data()
    for i, s in enumerate(data):
        if s["id"] == str(student_id):
            data.pop(i)
            _write_data(data)
            return
    raise HTTPException(status_code=404, detail="student not found")

@app.get("/students", response_model=List[Student])
def list_students(
    q: Optional[str] = Query(None, description="search by name or email"),
    department: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None, regex="^(name|age)$"),
    order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    limit: Optional[int] = Query(None, ge=1),
    offset: Optional[int] = Query(0, ge=0)
):
    data = _read_data()
    results = data
    if q:
        q_lower = q.lower()
        results = [s for s in results if q_lower in s.get("name","").lower() or q_lower in s.get("email","").lower()]
    if department is not None:
        results = [s for s in results if (s.get("department") or "") == department]
    if sort_by:
        reverse = order == "desc"
        results = sorted(results, key=lambda x: x.get(sort_by) or ("" if sort_by=="name" else 0), reverse=reverse)
    if offset:
        results = results[offset:]
    if limit is not None:
        results = results[:limit]
    return results

@app.get("/students/stats")
def students_stats():
    data = _read_data()
    total = len(data)
    avg_age = round(sum(s["age"] for s in data) / total, 2) if total > 0 else 0
    count_per_department = {}
    for s in data:
        dept = s.get("department") or "Unknown"
        count_per_department[dept] = count_per_department.get(dept, 0) + 1
    return {"total_students": total, "average_age": avg_age, "count_per_department": count_per_department}
