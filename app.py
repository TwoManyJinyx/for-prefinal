from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_studentform'

mysql = MySQL(app)


def init_db():
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                course VARCHAR(100) NOT NULL
            )
        ''')
        mysql.connection.commit()
        cursor.close()


@app.route("/")
def home():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, username, email, course FROM students ORDER BY id")
    students = cursor.fetchall()
    cursor.close()
    return render_template("home.html", students=students)


@app.route("/process_registration", methods=["POST"])
def process_registration():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    course = request.form.get('course', '').strip()

    if username and email and course:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO students (username, email, course) VALUES (%s, %s, %s)",
            (username, email, course),
        )
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('home'))

    return render_template("home.html", error="Please fill in all fields.", students=[])


@app.route("/search_student")
def search_student():
    username = request.args.get('username')
    if username:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM students WHERE username = %s", (username,))
        student = cursor.fetchone()
        cursor.close()
        if student:
            return f"Student found: {student}"
        return "Student not found."
    return "Please provide a username to search."


@app.route("/update_student")
def update_student():
    username = request.args.get('username')
    email = request.args.get('email')
    course = request.args.get('course')

    if username and (email or course):
        cursor = mysql.connection.cursor()
        if email:
            cursor.execute("UPDATE students SET email = %s WHERE username = %s", (email, username))
        if course:
            cursor.execute("UPDATE students SET course = %s WHERE username = %s", (course, username))
        mysql.connection.commit()
        cursor.close()
        return "Student information updated successfully!"
    return "Please provide a username and at least one field to update."


@app.route("/delete_student")
def delete_student():
    username = request.args.get('username')
    if username:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM students WHERE username = %s", (username,))
        mysql.connection.commit()
        cursor.close()
        return "Student deleted successfully!"
    return "Please provide a username to delete."


if __name__ == "__main__":
    init_db()
    app.run(debug=True)