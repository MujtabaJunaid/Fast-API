from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/student", response_class=HTMLResponse)
def get_student():
student_info = f"""
<html>
<body>
<h1>Student Information</h1>
<p><strong>Name:</strong> Mujtaba Junaid</p>
<p><strong>ID:</strong> 7873</p>
<p><strong>Field of Study:</strong> Computer Science and AI</p>
</body>
</html>
"""
return student_info


