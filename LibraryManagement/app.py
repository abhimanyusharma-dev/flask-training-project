from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)

# Session ke liye secret key
app.secret_key = "library-secret-key"


# =========================
# DATABASE INITIALIZATION
# =========================

def init_db():

    conn = sqlite3.connect("library.db")

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Issued books table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS issued_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT NOT NULL,
            book_name TEXT NOT NULL,
            book_number TEXT NOT NULL,
            student_name TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():
    return render_template("home.html")


# =========================
# SIGN UP
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]

        try:

            conn = sqlite3.connect("library.db")

            conn.execute(
                """
                INSERT INTO users (name, username, password)
                VALUES (?, ?, ?)
                """,
                (name, username, password)
            )

            conn.commit()
            conn.close()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            return "Username already exists!"

    return render_template("signup.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM users
            WHERE username = ? AND password = ?
            """,
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            # Login information session me save
            session["user_id"] = user[0]
            session["username"] = user[2]

            return redirect(url_for("dashboard"))

        else:

            return "Invalid username or password!"


    return render_template("login.html")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    # Agar login nahi hai
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")


# =========================
# ISSUE BOOK
# =========================

@app.route("/issue-book", methods=["GET", "POST"])
def issue_book():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        book_id = request.form["book_id"]
        book_name = request.form["book_name"]
        book_number = request.form["book_number"]
        student_name = request.form["student_name"]
        issue_date = request.form["issue_date"]
        due_date = request.form["due_date"]

        conn = sqlite3.connect("library.db")

        conn.execute(
            """
            INSERT INTO issued_books
            (
                book_id,
                book_name,
                book_number,
                student_name,
                issue_date,
                due_date
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                book_id,
                book_name,
                book_number,
                student_name,
                issue_date,
                due_date
            )
        )

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "success",
                book_name=book_name,
                student_name=student_name,
                issue_date=issue_date
            )
        )

    return render_template("issue_book.html")


# =========================
# SUCCESS PAGE
# =========================

@app.route("/success")
def success():

    book_name = request.args.get("book_name")
    student_name = request.args.get("student_name")
    issue_date = request.args.get("issue_date")

    return render_template(
        "success.html",
        book_name=book_name,
        student_name=student_name,
        issue_date=issue_date
    )


# =========================
# VIEW BOOKS
# =========================

@app.route("/view-books")
def view_books():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            book_id,
            book_name,
            book_number,
            student_name,
            issue_date,
            due_date
        FROM issued_books
    """)

    books = cursor.fetchall()

    conn.close()

    return render_template(
        "view_books.html",
        books=books
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    init_db()

    app.run(debug=True)