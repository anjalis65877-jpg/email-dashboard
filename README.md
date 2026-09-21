# Email Dashboard Automation Project

## 1. Install Python
Install Python 3.10 or newer.

## 2. Open terminal in this folder

## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Run the project
```bash
python app.py
```

## 5. Open in browser
Go to:
http://127.0.0.1:5000

## Features
- Dashboard with email counts
- Inbox and Sent pages
- Search emails
- Open individual emails
- Compose and save demo emails
- Optional SMTP sending

## Optional real email sending
Do not put your Gmail password directly in the code. Use an app password or a secure email provider.

Windows PowerShell example:
```powershell
$env:SEND_REAL_EMAILS="true"
$env:SMTP_USER="your_email@gmail.com"
$env:SMTP_PASSWORD="your_app_password"
python app.py
```

This starter version uses demo email data and SQLite. Gmail API OAuth can be added as the next project level.
