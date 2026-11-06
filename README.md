# Bank Management System

A simple and interactive **Bank Management System** built using Python and Streamlit. This application simulates basic banking operations, allowing users to create accounts, manage their balances, transfer money, and view transaction history through a user-friendly interface.

## About the Project

The Bank Management System is a Python-based web application designed to demonstrate how basic banking operations can be implemented using programming concepts, data handling, and a graphical user interface.

The application provides separate user access through registration and login. Once logged in, users can manage their accounts and perform different banking operations.

## Features

- **User Registration:** Create a new bank account through the registration process.
- **User Login:** Secure login using registered credentials.
- **Dashboard:** View account information and balance.
- **Deposit Money:** Add money to an account.
- **Withdraw Money:** Withdraw money while checking available balance.
- **Money Transfer:** Transfer funds between registered accounts.
- **Transaction History:** View records of deposits, withdrawals, and transfers.
- **My Profile:** View personal account information.
- **Account Management:** Automatically generate unique account numbers.
- **Data Storage:** Store user, account, and transaction information using JSON.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic and backend functionality |
| Streamlit | User interface and web application |
| JSON | Data storage |
| HTML & CSS | Interface styling through Streamlit |

## 📂 Project Structure

```text
BankManagementSystem/
│
├── .streamlit/
│   └── config.toml
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── bank_data.json
```

**Note:** `bank_data.json` is generated locally when the application needs it and is excluded from GitHub to avoid exposing user data.

## ⚙️ Installation and Setup

Follow these steps to run the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/ArpitaSaha2004/BankManagementSystem.git
```

### 2. Navigate to the Project Directory

```bash
cd BankManagementSystem
```

### 3. Create a Virtual Environment

```bash
python3 -m venv .venv
```

### 4. Activate the Virtual Environment

For macOS / Linux:

```bash
source .venv/bin/activate
```

For Windows:

```bash
.venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser, usually at:

```text
http://localhost:8501
```

## Data and Security

- Passwords are stored as password hashes rather than plain text.
- User and transaction data are stored in a local JSON file.
- The JSON database is excluded from version control using `.gitignore`.

## Author

**Arpita Saha**
