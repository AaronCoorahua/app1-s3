from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
import sqlite3

app = Flask(__name__)
api = Api(app, version='1.0', title='Student API', description='A simple API for managing students')

ns = api.namespace('students', description='Operations related to students')

student_model = api.model('Student', {
    'firstname': fields.String(required=True, description='First name of the student'),
    'lastname': fields.String(required=True, description='Last name of the student'),
    'gender': fields.String(required=True, description='Gender of the student'),
    'age': fields.Integer(required=True, description='Age of the student')
})

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect('students.sqlite')
    except sqlite3.error as e:
        print(e)
    return conn

@ns.route('/')
class Students(Resource):
    def get(self):
        """List all students"""
        conn = db_connection()
        cursor = conn.execute("SELECT * FROM students")
        students = [
            dict(id=row[0], firstname=row[1], lastname=row[2], gender=row[3], age=row[4])
            for row in cursor.fetchall()
        ]
        return jsonify(students)

    @api.expect(student_model)
    def post(self):
        """Create a new student"""
        conn = db_connection()
        cursor = conn.cursor()
        new_student = request.json if request.is_json else request.form
        sql = """INSERT INTO students (firstname, lastname, gender, age) VALUES (?, ?, ?, ?)"""
        cursor.execute(sql, (new_student['firstname'], new_student['lastname'], new_student['gender'], new_student['age']))
        conn.commit()
        return {"result": f"Student with id: {cursor.lastrowid} created successfully"}, 201

@ns.route('/<int:id>')
@api.response(404, 'Student not found')
class Student(Resource):
    def get(self, id):
        """Fetch a student given their ID"""
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id=?", (id,))
        row = cursor.fetchone()
        if row:
            return jsonify(dict(id=row[0], firstname=row[1], lastname=row[2], gender=row[3], age=row[4]))
        api.abort(404, "Student not found")

    @api.expect(student_model)
    def put(self, id):
        """Update a student given their ID"""
        conn = db_connection()
        student = request.json if request.is_json else request.form
        sql = """UPDATE students SET firstname=?, lastname=?, gender=?, age=? WHERE id=?"""
        conn.execute(sql, (student['firstname'], student['lastname'], student['gender'], student['age'], id))
        conn.commit()
        return jsonify(student)

    def delete(self, id):
        """Delete a student given their ID"""
        conn = db_connection()
        sql = """DELETE FROM students WHERE id=?"""
        conn.execute(sql, (id,))
        conn.commit()
        return {"result": f"The student with id: {id} has been deleted"}, 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
