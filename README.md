# Student API

A FastAPI application for managing and retrieving student information.

## Features

- Retrieve all students
- Get student by ID
- Get students sorted by CGPA
- JSON-based data storage
- Proper HTTP status code handling

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install fastapi uvicorn

# Running the Application
## Start the server using:
uvicorn main:app --reload

## API Endpoints
## Get All Students
URL: /students

Method: GET

Response: Returns all students data

Status Code: 200

## Get Student by ID

URL: /students

Method: GET

Response: Returns all students data

Status Code: 200x

## Get Sorted Students

URL: /students/sorted?sort_by=cgpa

Method: GET

Query Parameter: sort_by (must be "cgpa")

Response: Returns students sorted by CGPA in descending order

Status Code: 200 (Success), 400 (Bad Request)

## Data Structure
Each student object contains:

id: Student identification number

name: Full name of student

field_of_study: Academic discipline

cgpa: Cumulative Grade Point Average

## Example Usage

curl http://localhost:8000/students
curl http://localhost:8000/student/7873
curl http://localhost:8000/students/sorted?sort_by=cgpa

## Project Structure

project/
├── main.py
├── students.json
└── README.md
