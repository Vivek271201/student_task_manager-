from flask import Flask, render_template, request, redirect, url_for, session, flash

from db_config import get_db_connection


# -------------------------------------
# Create Flask Application
# -------------------------------------

app = Flask(__name__)

# Secret key for session management
app.secret_key = "Vivek2709"


# -------------------------------------
# Home Route
# -------------------------------------

@app.route('/')
def home():
    return redirect(url_for('login'))


# -------------------------------------
# Login Page Route
# -------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT *
        FROM users
        WHERE username=%s
        AND password=%s
        """

        cursor.execute(query, (username, password))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:

            session['user_id'] = user['user_id']
            session['username'] = user['username']

            return redirect(url_for('index'))

        else:

            flash("Invalid Username or Password")

    return render_template('login.html')


# -------------------------------------
# Logout Route
# -------------------------------------
@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('login'))


# -------------------------------------
# Students Page Route
# -------------------------------------
@app.route('/students')
def students():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'students.html',
        students=students
    )
# -------------------------------------
# Index Page Route
# -------------------------------------
@app.route('/index')
def index():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Total Students
    cursor.execute("SELECT COUNT(*) AS total_students FROM students")
    total_students = cursor.fetchone()['total_students']

    # Total Attendance Records
    cursor.execute("SELECT COUNT(*) AS total_attendance FROM attendance")
    total_attendance = cursor.fetchone()['total_attendance']

    # Total Tasks
    cursor.execute("SELECT COUNT(*) AS total_tasks FROM tasks")
    total_tasks = cursor.fetchone()['total_tasks']

    cursor.close()
    conn.close()

    return render_template(
        'index.html',
        total_students=total_students,
        total_attendance=total_attendance,
        total_tasks=total_tasks
    )


#add student route
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        mobile_number = request.form['mobile_number']
        email = request.form['email']
        course_name = request.form['course_name']
        admission_date = request.form['admission_date']

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO students
        (
            first_name,
            last_name,
            gender,
            mobile_number,
            email,
            course_name,
            admission_date
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            first_name,
            last_name,
            gender,
            mobile_number,
            email,
            course_name,
            admission_date
        )

        cursor.execute(query, values)

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('students'))

    return render_template('add_student.html')


# Attendance
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':

        student_id = request.form['student_id']
        attendance_date = request.form['attendance_date']
        status = request.form['status']

        insert_query = """
        INSERT INTO attendance
        (
            student_id,
            attendance_date,
            status
        )
        VALUES (%s,%s,%s)
        """

        cursor.execute(
            insert_query,
            (
                student_id,
                attendance_date,
                status
            )
        )

        conn.commit()

        return redirect(url_for('attendance_report'))

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'attendance.html',
        students=students
    )

#attendance report route

@app.route('/attendance_report')
def attendance_report():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT
        attendance.attendance_id,
        attendance.attendance_date,
        attendance.status,

        students.first_name,
        students.last_name

    FROM attendance

    INNER JOIN students
    ON attendance.student_id = students.student_id

    ORDER BY attendance.attendance_date DESC
    """

    cursor.execute(query)

    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'attendance_report.html',
        records=records
    )


@app.route('/add_task', methods=['GET', 'POST'])
def add_task():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        task_name = request.form['task_name']
        task_description = request.form['task_description']
        maximum_marks = request.form['maximum_marks']

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO tasks
        (
            task_name,
            task_description,
            maximum_marks
        )
        VALUES (%s,%s,%s)
        """

        cursor.execute(
            query,
            (
                task_name,
                task_description,
                maximum_marks
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('tasks'))

    return render_template('add_task.html')


@app.route('/tasks')
def tasks():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tasks")

    tasks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'tasks.html',
        tasks=tasks
    )

@app.route('/assign_task', methods=['GET', 'POST'])
def assign_task():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':

        student_id = request.form['student_id']
        task_id = request.form['task_id']

        insert_query = """
        INSERT INTO assigned_tasks
        (
            student_id,
            task_id
        )
        VALUES (%s,%s)
        """

        cursor.execute(
            insert_query,
            (
                student_id,
                task_id
            )
        )

        conn.commit()

        return redirect(url_for('assigned_tasks'))

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'assign_task.html',
        students=students,
        tasks=tasks
    )

@app.route('/assigned_tasks')
def assigned_tasks():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT

        assigned_tasks.assigned_id,

        students.first_name,
        students.last_name,

        tasks.task_name,
        tasks.maximum_marks

    FROM assigned_tasks

    INNER JOIN students
    ON assigned_tasks.student_id = students.student_id

    INNER JOIN tasks
    ON assigned_tasks.task_id = tasks.task_id
    """

    cursor.execute(query)

    assignments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'assigned_tasks.html',
        assignments=assignments
    )



#edit student route
@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)   

    if request.method == 'POST':

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        mobile_number = request.form['mobile_number']
        email = request.form['email']
        course_name = request.form['course_name']
        admission_date = request.form['admission_date']

        update_query = """
        UPDATE students
        SET
            first_name=%s,
            last_name=%s,
            gender=%s,
            mobile_number=%s,
            email=%s,
            course_name=%s,
            admission_date=%s
        WHERE student_id=%s
        """

        cursor.execute(
            update_query,
            (
                first_name,
                last_name,
                gender,
                mobile_number,
                email,
                course_name,
                admission_date,
                student_id
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('students'))

    cursor.execute(
        "SELECT * FROM students WHERE student_id=%s",
        (student_id,)
    )

    student = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        'edit_student.html',
        student=student
    )

#delete student route
@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE student_id=%s",
        (student_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('students'))

# -------------------------------------
# Run Flask App
# -------------------------------------

if __name__ == "__main__":
    app.run(debug=True)