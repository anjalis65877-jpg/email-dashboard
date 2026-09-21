from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
from email.message import EmailMessage
import smtplib
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")
DB_NAME = "emails.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            status TEXT DEFAULT 'Inbox',
            created_at TEXT NOT NULL
        )
    """)
    count = conn.execute("SELECT COUNT(*) AS total FROM emails").fetchone()["total"]
    if count == 0:
        demo_emails = [
            ("hr@example.com", "you@example.com", "Interview Invitation",
             "Your interview has been scheduled for Monday.", "Inbox"),
            ("learn@example.com", "you@example.com", "Python Practice",
             "Continue practicing Python and SQL every day.", "Inbox"),
            ("you@example.com", "friend@example.com", "Project Update",
             "I have completed the first version of the project.", "Sent")
        ]
        conn.executemany("""
            INSERT INTO emails
            (sender, recipient, subject, body, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [(a,b,c,d,e,datetime.now().strftime("%Y-%m-%d %H:%M"))
              for a,b,c,d,e in demo_emails])
    conn.commit()
    conn.close()

@app.route("/")
def dashboard():
    conn = get_db()
    inbox_count = conn.execute(
        "SELECT COUNT(*) AS total FROM emails WHERE status='Inbox'"
    ).fetchone()["total"]
    sent_count = conn.execute(
        "SELECT COUNT(*) AS total FROM emails WHERE status='Sent'"
    ).fetchone()["total"]
    all_count = conn.execute(
        "SELECT COUNT(*) AS total FROM emails"
    ).fetchone()["total"]
    recent = conn.execute(
        "SELECT * FROM emails ORDER BY id DESC LIMIT 5"
    ).fetchall()
    conn.close()
    return render_template(
        "dashboard.html",
        inbox_count=inbox_count,
        sent_count=sent_count,
        all_count=all_count,
        recent=recent
    )

@app.route("/inbox")
def inbox():
    conn = get_db()
    emails = conn.execute(
        "SELECT * FROM emails WHERE status='Inbox' ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template("inbox.html", emails=emails, title="Inbox")

@app.route("/sent")
def sent():
    conn = get_db()
    emails = conn.execute(
        "SELECT * FROM emails WHERE status='Sent' ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template("inbox.html", emails=emails, title="Sent")

@app.route("/email/<int:email_id>")
def view_email(email_id):
    conn = get_db()
    email = conn.execute(
        "SELECT * FROM emails WHERE id=?", (email_id,)
    ).fetchone()
    conn.close()
    if email is None:
        flash("Email not found.")
        return redirect(url_for("dashboard"))
    return render_template("view_email.html", email=email)

@app.route("/compose", methods=["GET", "POST"])
def compose():
    if request.method == "POST":
        recipient = request.form.get("recipient", "").strip()
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()

        if not recipient or not subject or not body:
            flash("Please fill in all fields.")
            return redirect(url_for("compose"))

        conn = get_db()
        conn.execute("""
            INSERT INTO emails
            (sender, recipient, subject, body, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "you@example.com",
            recipient,
            subject,
            body,
            "Sent",
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))
        conn.commit()
        conn.close()

        # Optional real email sending:
        # Configure SMTP_USER, SMTP_PASSWORD and SMTP_HOST in your environment.
        if os.getenv("SEND_REAL_EMAILS", "false").lower() == "true":
            try:
                send_real_email(recipient, subject, body)
                flash("Email saved and sent successfully.")
            except Exception as error:
                flash(f"Email saved, but real sending failed: {error}")
        else:
            flash("Demo email saved successfully. Real sending is disabled.")

        return redirect(url_for("sent"))

    return render_template("compose.html")

def send_real_email(recipient, subject, body):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.environ["SMTP_USER"]
    smtp_password = os.environ["SMTP_PASSWORD"]

    message = EmailMessage()
    message["From"] = smtp_user
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(message)

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    conn = get_db()
    emails = conn.execute("""
        SELECT * FROM emails
        WHERE subject LIKE ? OR sender LIKE ? OR body LIKE ?
        ORDER BY id DESC
    """, (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
    conn.close()
    return render_template("inbox.html", emails=emails, title=f"Search: {query}")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
