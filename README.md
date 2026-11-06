# Bank Management System

A beginner-friendly banking simulation built with Python, Streamlit and JSON.

## Features

- Customer registration and login
- Password hashing (PBKDF2-HMAC-SHA256)
- Automatically generated account numbers
- Dashboard with account balance
- Deposit and withdrawal
- Transfers between demo accounts
- Transaction history
- JSON file storage

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment:

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   **Windows**
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the app:

   ```bash
   streamlit run app.py
   ```

Streamlit will print a local URL, usually http://localhost:8501.

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload `app.py`, `requirements.txt`, `README.md` and `bank_data.json`.
3. Do not upload real customer data. Keep `bank_data.json` empty.
4. Sign in at https://share.streamlit.io/ using GitHub.
5. Select the repository and set the main file path to `app.py`.
6. Deploy.

### Important JSON hosting limitation

Streamlit Community Cloud is not a durable database host. Files written by an app may be lost when the app restarts, redeploys or its environment is replaced. A JSON file is also not safe for concurrent writes from multiple users. This deployment is suitable only as a demonstration with disposable sample data. For persistent multi-user deployment, replace JSON storage with a hosted database such as PostgreSQL.

## Security and scope

This is an educational portfolio simulation only. It does not connect to banks, payment networks or real financial accounts. Do not enter real personal information, reuse passwords, or deposit real money. Passwords are hashed before being stored, but JSON-file storage is not suitable for production banking or sensitive customer records.
