from fastapi import FastAPI, HTTPException, Query
import json
from typing import List, Optional

app = FastAPI()

with open('students_Task2.json', 'r') as file:
    data = json.load(file)
    students = data['students']

@app.get("/students", status_code=200)
def get_all_students():
    return {"students": students}

@app.get("/student/{student_id}", status_code=200)
def get_student_by_id(student_id: int):
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.get("/students/sorted", status_code=200)
def get_sorted_students(sort_by: Optional[str] = Query("cgpa")):
    if sort_by != "cgpa":
        raise HTTPException(status_code=400, detail="Sorting only available by CGPA")
    
    sorted_students = sorted(students, key=lambda x: x["cgpa"], reverse=True)
    return {"students": sorted_students}
