from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import json
from pathlib import Path

app = FastAPI()

DATA_FILE = "students.json"

class Student(BaseModel):
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=2, max_length=50)
    age: int = Field(..., gt=5, lt=100)
    roll_number: str
    grade: Optional[str] = None

    @validator('name')
    def name_cannot_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v

def load_students() -> List[dict]:
    if Path(DATA_FILE).exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_students(students: List[dict]):
    with open(DATA_FILE, 'w') as f:
        json.dump(students, f, indent=2)

@app.post("/students/")
def add_student(student: Student):
    students = load_students()
    
    if any(s['id'] == student.id for s in students):
        raise HTTPException(status_code=400, detail="Student ID already exists")
    
    if any(s['roll_number'] == student.roll_number for s in students):
        raise HTTPException(status_code=400, detail="Roll number already exists")
    
    student_dict = student.dict()
    students.append(student_dict)
    save_students(students)
    
    return student_dict

@app.get("/students/")
def get_all_students():
    return load_students()

@app.get("/students/{student_id}")
def get_student(student_id: int):
    students = load_students()
    student = next((s for s in students if s['id'] == student_id), None)
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student
