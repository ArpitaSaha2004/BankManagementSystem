
import streamlit as st
import json
import os
import secrets
import hashlib
import hmac
import html
import tempfile
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation

st.set_page_config(
    page_title="Bank Management System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_FILE = Path(__file__).parent / "bank_data.json"


def empty_data():
    return {
        "users": {},
        "accounts": {},
        "transactions": []
    }

def load_data():
    if not DATA_FILE.exists():
        return empty_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        data.setdefault("users", {})
        data.setdefault("accounts", {})
        data.setdefault("transactions", [])
        return data
    except (json.JSONDecodeError, OSError):
        st.error("Unable to read bank_data.json.")
        return empty_data()

def save_data(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=DATA_FILE.parent,
            delete=False,
            suffix=".tmp"
        ) as temp_file:
            json.dump(data, temp_file, indent=4)
            temp_name = temp_file.name
        os.replace(temp_name, DATA_FILE)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.remove(temp_name)

def hash_password(password):
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200000
    )
    return (
        salt.hex()
        + ":"
        + password_hash.hex()
    )

def verify_password(password, stored_hash):
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200000
        )
        return hmac.compare_digest(
            actual_hash,
            expected_hash
        )
    except (ValueError, TypeError):
        return False

def new_account_number(data):
    while True:
        account_number = str(
            secrets.randbelow(90000000) + 10000000
        )
        if account_number not in data["accounts"]:
            return account_number

def create_account(name, email, password):
    data = load_data()
    email_key = email.strip().lower()
    if email_key in data["users"]:
        return False, "An account with this email already exists."
    account_number = new_account_number(data)
    created_at = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )
    data["users"][email_key] = {
        "name": name.strip(),
        "email": email_key,
        "password_hash": hash_password(password),
        "account_number": account_number,
        "created_at": created_at
    }

    data["accounts"][account_number] = {
        "account_number": account_number,
        "email": email_key,
        "balance": "0.00",
        "status": "active"
    }
    save_data(data)
    return True, account_number

def authenticate(email, password):
    data = load_data()
    email_key = email.strip().lower()
    user = data["users"].get(email_key)
    if user and verify_password(
        password,
        user.get("password_hash", "")
    ):
        return user
    return None

def money_value(value):
    try:
        amount = Decimal(str(value).strip())
        if not amount.is_finite() or amount <= 0:
            return None
        if amount.as_tuple().exponent < -2:
            return None
        return amount.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError, TypeError):
        return None


def money_text(amount):
    return f"₹{Decimal(str(amount)):,.2f}"

def add_transaction(
    data,
    account_number,
    kind,
    amount,
    note,
    balance_after
):
    data["transactions"].append({
        "transaction_id": secrets.token_hex(6).upper(),
        "account_number": account_number,
        "type": kind,
        "amount": f"{amount:.2f}",
        "note": note,
        "balance_after": f"{balance_after:.2f}",
        "created_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        )
    })

st.markdown("""
<style>

:root {
    --ink: #172b4d;
    --muted: #718096;
    --accent: #167d79;
}

.stApp {
    background: #f5f7fb;
    color: var(--ink);
}

[data-testid="stHeader"] {
    background: rgba(244,247,248,.92);
}

[data-testid="stSidebar"] {
    background: #101d35;
    border-right: 1px solid rgba(255,255,255,.08);
}

[data-testid="stSidebar"] * {
    color: #f4f8fb !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 7px 0;
}

[data-testid="stSidebar"] [data-testid="stButton"] button {
    background: rgba(255,255,255,.10);
    border: 1px solid rgba(255,255,255,.18);
}

.brand {
    color: #17334f;
    font-size: 2rem;
    line-height: 1.15;
    font-weight: 800;
    letter-spacing: -.7px;
    margin-bottom: 4px;
}

.brand-mark {
    display: inline-flex;
    width: 46px;
    height: 46px;
    border-radius: 14px;
    align-items: center;
    justify-content: center;
    background: #e1f1ef;
    color: #1d5688;
    font-size: 1.45rem;
    margin-bottom: 15px;
}

div[data-testid="stMetric"] {
    background: #fff;
    padding: 20px 21px;
    border-radius: 16px;
    border: 1px solid #e5ebef;
    box-shadow: 0 5px 18px rgba(25,48,70,.045);
}

[data-testid="stMetricLabel"] {
    color: #718096;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #17334f;
    font-weight: 750;
}

.welcome-card {
    background: linear-gradient(120deg, #17345c 0%, #285b8f 100%);
    color: white;
    padding: 30px 32px;
    border-radius: 20px;
    margin: 8px 0 24px 0;
    box-shadow: 0 12px 28px rgba(23,51,79,.13);
}

.welcome-card h2 {
    color: white;
    margin: 0 0 7px 0;
    font-size: 1.75rem;
}

.welcome-card p {
    color: #d9e9eb;
    margin: 0;
}

.stButton > button,
[data-testid="stFormSubmitButton"] button {
    border-radius: 10px;
    min-height: 2.7rem;
    font-weight: 650;
    border: 1px solid #dce5e9;
}

.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"] {
    background: #167d79;
    border-color: #167d79;
    color: white;
}

.stButton > button:hover {
    border-color: #1d5688;
    color: #126a67;
}

[data-testid="stTextInput"] input {
    border-radius: 10px;
    background: white;
}

[data-testid="stDataFrame"] {
    border: 1px solid #e5ebef;
    border-radius: 12px;
    overflow: hidden;
}

.author-credit {
    position: fixed;
    bottom: 12px;
    right: 25px;
    color: #82909d;
    font-size: .78rem;
    letter-spacing: .3px;
    font-weight: 600;
    z-index: 999;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

st.session_state.setdefault("user_email", None)
st.session_state.setdefault("flash_message", None)

def show_flash():
    message = st.session_state.get("flash_message")
    if message:
        kind, text = message
        getattr(st, kind)(text)
        st.session_state.flash_message = None

def logout():
    st.session_state.user_email = None
    st.session_state.flash_message = (
        "success",
        "You have been logged out."
    )
    st.rerun()

def render_auth():
    left, center, right = st.columns([1, 1.35, 1])

    with center:
        st.markdown(
            '<div class="brand-mark">🏦</div>'
            '<div class="brand">Bank Management System</div>',
            unsafe_allow_html=True
        )
        st.caption("Your banking, made simple.")
        login_tab, register_tab = st.tabs(
            ["Login", "Create account"]
        )
        
        with login_tab:
            st.subheader("Welcome back")
            with st.form("login_form"):
                email = st.text_input(
                    "Email address",
                    placeholder="you@example.com"
                )
                password = st.text_input(
                    "Password",
                    type="password"
                )
                submitted = st.form_submit_button(
                    "Sign in",
                    use_container_width=True
                )
            if submitted:
                if not email.strip() or not password:
                    st.error("Enter your email and password.")
                else:
                    user = authenticate(email, password)
                    if user:
                        st.session_state.user_email = user["email"]
                        st.session_state.flash_message = (
                            "success",
                            "Login successful."
                        )
                        st.rerun()
                    else:
                        st.error("Email or password is incorrect.")

        with register_tab:
            st.subheader("Create your account")
            with st.form("register_form"):
                name = st.text_input("Full name")
                new_email = st.text_input(
                    "Email address",
                    key="register_email"
                )
                new_password = st.text_input(
                    "Password",
                    type="password",
                    key="register_password"
                )
                confirm_password = st.text_input(
                    "Confirm password",
                    type="password"
                )
                submitted = st.form_submit_button(
                    "Create account",
                    use_container_width=True
                )
            if submitted:
                if (
                    not name.strip()
                    or not new_email.strip()
                    or not new_password
                ):
                    st.error("Please complete all fields.")
                elif (
                    "@" not in new_email
                    or "." not in new_email.split("@")[-1]
                ):
                    st.error("Enter a valid email address.")
                elif len(new_password) < 8:
                    st.error(
                        "Use a password with at least 8 characters."
                    )
                elif new_password != confirm_password:
                    st.error("The passwords do not match.")
                else:
                    ok, result = create_account(
                        name,
                        new_email,
                        new_password
                    )
                    if ok:
                        st.success(
                            f"Account created successfully! "
                            f"Your account number is {result}. "
                            "Please sign in."
                        )
                    else:
                        st.error(result)

def render_dashboard(user):

    data = load_data()
    account_number = user["account_number"]
    account = data["accounts"].get(account_number)
    if not account:
        st.error("Account information could not be found.")
        logout()
        return
    balance = Decimal(str(account["balance"]))
    account_transactions = [
        transaction
        for transaction in data["transactions"]
        if (
            transaction.get("account_number") == account_number
            or transaction.get("related_account") == account_number
        )
    ]
    account_transactions.sort(
        key=lambda transaction: transaction.get("created_at", ""),
        reverse=True
    )
    st.sidebar.markdown(
        """
        <div style="padding:12px 0 20px 0;">
            <div style="font-size:28px;">🏦</div>
            <h3 style="color:white;margin:5px 0;">
                BANK MANAGEMENT SYSTEM
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.divider()
    st.sidebar.markdown("### MAIN MENU")
    page = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Deposit Money",
            "Withdraw Money",
            "Transfer Money",
            "Transaction History",
            "My Profile"
        ],
        label_visibility="collapsed"
    )
    st.sidebar.divider()
    st.sidebar.markdown("### ACCOUNT")
    st.sidebar.write(f"👤 {user['name']}")
    st.sidebar.caption(f"Account No: {account_number}")
    if st.sidebar.button("Log out", use_container_width=True):
        logout()

    if page == "Dashboard":

        safe_name = html.escape(user["name"])
        st.markdown(
            f"""
            <div class="welcome-card">
                <h2>Hello, {safe_name} 👋</h2>
                <p>Welcome back! Here's your account overview.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("Account Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Available Balance",
            money_text(balance)
        )
        col2.metric(
            "Account Number",
            account_number
        )
        col3.metric(
            "Total Transactions",
            len(account_transactions)
        )
        st.write("")
        st.subheader("Recent Transactions")
        if account_transactions:
            for transaction in account_transactions[:5]:
                transaction_type = transaction.get(
                    "type",
                    "Transaction"
                )
                incoming = transaction_type in [
                    "Deposit",
                    "Transfer received"
                ]
                amount = Decimal(
                    str(transaction.get("amount", "0"))
                )
                note = transaction.get("note", "")
                created_at = transaction.get("created_at", "")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{transaction_type}**")
                    st.caption(note)
                    st.caption(created_at)
                with col2:
                    if incoming:
                        st.markdown(
                            f"""
                            <div style="
                                text-align:right;
                                color:#167d79;
                                font-weight:700;
                                padding-top:8px;
                            ">
                                +{money_text(amount)}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <div style="
                                text-align:right;
                                color:#c45b5b;
                                font-weight:700;
                                padding-top:8px;
                            ">
                                -{money_text(amount)}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                st.divider()
        else:
            st.info(
                "No transactions yet. Make your first deposit to get started."
            )

    elif page == "Deposit Money":
        st.title("Deposit Money")
        st.caption("Add money to your bank account.")

        with st.form("deposit_form"):
            amount_input = st.text_input(
                "Amount (₹)",
                placeholder="Enter amount"
            )
            note = st.text_input(
                "Description",
                placeholder="Cash deposit"
            )
            submitted = st.form_submit_button(
                "Deposit Money",
                type="primary",
                use_container_width=True
            )

        if submitted:
            amount = money_value(amount_input)
            if amount is None:
                st.error("Enter a valid amount greater than zero.")
            else:
                data = load_data()
                account = data["accounts"].get(account_number)
                if not account:
                    st.error("Account not found.")
                elif account.get("status") != "active":
                    st.error("This account is not active.")
                else:
                    new_balance = (
                        Decimal(str(account["balance"])) + amount
                    )
                    account["balance"] = f"{new_balance:.2f}"

                    add_transaction(
                        data,
                        account_number,
                        "Deposit",
                        amount,
                        note.strip() or "Cash deposit",
                        new_balance
                    )

                    save_data(data)
                    st.session_state.flash_message = (
                        "success",
                        f"Deposit successful! New balance: "
                        f"{money_text(new_balance)}"
                    )
                    st.rerun()

    elif page == "Withdraw Money":
        st.title("Withdraw Money")
        st.caption("Withdraw money from your account.")

        with st.form("withdraw_form"):
            amount_input = st.text_input(
                "Amount (₹)",
                placeholder="Enter amount"
            )
            note = st.text_input(
                "Description",
                placeholder="ATM withdrawal"
            )
            submitted = st.form_submit_button(
                "Withdraw Money",
                type="primary",
                use_container_width=True
            )
        if submitted:

            amount = money_value(amount_input)
            if amount is None:
                st.error("Enter a valid amount greater than zero.")
            else:
                data = load_data()
                account = data["accounts"].get(account_number)
                if not account:
                    st.error("Account not found.")
                elif account.get("status") != "active":
                    st.error("This account is not active.")
                else:
                    current_balance = Decimal(
                        str(account["balance"])
                    )
                    if amount > current_balance:

                        st.error("Insufficient balance.")
                    else:
                        new_balance = current_balance - amount
                        account["balance"] = f"{new_balance:.2f}"
                        add_transaction(
                            data,
                            account_number,
                            "Withdrawal",
                            amount,
                            note.strip() or "Cash withdrawal",
                            new_balance
                        )

                        save_data(data)
                        st.session_state.flash_message = (
                            "success",
                            f"Withdrawal successful! Remaining balance: "
                            f"{money_text(new_balance)}"
                        )
                        st.rerun()

    elif page == "Transfer Money":
        st.title("Transfer Money")
        st.caption("Send money to another bank account.")
        with st.form("transfer_form"):
            recipient = st.text_input(
                "Recipient Account Number",
                placeholder="Enter 8-digit account number",
                max_chars=8
            )
            amount_input = st.text_input(
                "Amount (₹)",
                placeholder="Enter amount"
            )
            note = st.text_input(
                "Description",
                placeholder="Personal transfer"
            )
            submitted = st.form_submit_button(
                "Transfer Money",
                type="primary",
                use_container_width=True
            )
        if submitted:
            amount = money_value(amount_input)
            recipient = recipient.strip()
            data = load_data()
            source = data["accounts"].get(account_number)
            destination = data["accounts"].get(recipient)
            if (
                not recipient.isdigit()
                or len(recipient) != 8
                or not destination
            ):
                st.error(
                    "Recipient account was not found. "
                    "Enter a valid 8-digit account number."
                )
            elif recipient == account_number:
                st.error(
                    "You cannot transfer money to your own account."
                )
            elif amount is None:
                st.error("Enter a valid amount greater than zero.")
            elif not source or source.get("status") != "active":
                st.error("Your account is not active.")
            elif destination.get("status") != "active":
                st.error("Recipient account is not active.")
            elif amount > Decimal(str(source["balance"])):
                st.error("Insufficient balance.")
            else:
                source_balance = (
                    Decimal(str(source["balance"])) - amount
                )
                destination_balance = (
                    Decimal(str(destination["balance"])) + amount
                )
                source["balance"] = f"{source_balance:.2f}"
                destination["balance"] = f"{destination_balance:.2f}"
                timestamp = datetime.now().astimezone().isoformat(
                    timespec="seconds"
                )
                transfer_id = secrets.token_hex(6).upper()
                description = note.strip() or "Money transfer"

                data["transactions"].append({
                    "transaction_id": transfer_id,
                    "account_number": account_number,
                    "related_account": recipient,
                    "type": "Transfer sent",
                    "amount": f"{amount:.2f}",
                    "note": description,
                    "balance_after": f"{source_balance:.2f}",
                    "created_at": timestamp
                })

                data["transactions"].append({
                    "transaction_id": transfer_id,
                    "account_number": recipient,
                    "related_account": account_number,
                    "type": "Transfer received",
                    "amount": f"{amount:.2f}",
                    "note": description,
                    "balance_after": f"{destination_balance:.2f}",
                    "created_at": timestamp
                })
                save_data(data)
                st.session_state.flash_message = (
                    "success",
                    f"Transfer successful! {money_text(amount)} sent."
                )
                st.rerun()

    elif page == "Transaction History":
        st.title("Transaction History")
        st.caption("View all your account transactions.")
        if account_transactions:
            rows = []
            for transaction in account_transactions:
                rows.append({
                    "Date": transaction.get("created_at", ""),
                    "Type": transaction.get("type", ""),
                    "Description": transaction.get("note", ""),
                    "Amount (₹)": float(
                        transaction.get("amount", 0)
                    ),
                    "Balance after (₹)": float(
                        transaction.get("balance_after", 0)
                    ),
                    "Transaction ID": transaction.get(
                        "transaction_id", ""
                    )
                })
            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(
                "Your transaction history will appear here."
            )

    elif page == "My Profile":

        st.title("My Profile")
        st.caption("Your personal account information.")
        st.subheader("Account Information")
        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "Full Name",
                value=user.get("name", ""),
                disabled=True
            )
            st.text_input(
                "Email Address",
                value=user.get("email", ""),
                disabled=True
            )

        with col2:
            st.text_input(
                "Account Number",
                value=account_number,
                disabled=True
            )
            st.text_input(
                "Account Status",
                value=account.get("status", "active").title(),
                disabled=True
            )
        st.write("")
        st.subheader("Account Summary")
        st.metric(
            "Current Balance",
            money_text(balance)
        )
        st.caption(
            f"Account Created: {user.get('created_at', 'Not available')}"
        )
        st.caption("Profile details are read-only.")

show_flash()

if st.session_state.user_email:
    current_data = load_data()
    current_user = current_data["users"].get(
        st.session_state.user_email
    )

    if current_user:
        render_dashboard(current_user)
    else:
        st.session_state.user_email = None
        render_auth()
else:
    render_auth()


st.markdown(
    """
    <div class="author-credit">
        By Arpita
    </div>
    """,
    unsafe_allow_html=True
)
