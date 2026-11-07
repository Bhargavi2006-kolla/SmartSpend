import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, timedelta
from authorization import register_user, login_user
from expense_logic import (
    add_transaction,
    get_transactions,
    update_transaction,
    delete_transaction
)
from calculations import get_totals
from data import get_connection
from budget_logic import save_monthly_budget, get_monthly_budget
from analytics import (
    get_category_totals,
    get_monthly_totals,
    get_income_expense_totals
)

st.set_page_config(page_title="SmartSpend", page_icon="💜", layout="centered")

PAGES = [
    "Login",
    "Registration",
    "Dashboard",
    "Add Transaction",
    "History",
    "Budget",
    "Analysis"
]

PALETTE = ["#6D3FD8", "#A78BFA", "#C4B5FD", "#1E1B4B", "#F472B6", "#7C3AED"]

CATEGORY_ICONS = {
    "Salary": "💼",
    "Food": "🍴",
    "Travel": "🚌",
    "Shopping": "🛍️",
    "Bills": "🧾",
    "Other": "🎁"
}

# ---------- Session state setup ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "Login"

if "flash_message" not in st.session_state:
    st.session_state.flash_message = None

# Apply a pending navigation request BEFORE the sidebar radio is created.
# Streamlit does not allow changing a widget's key after it has been created in the same run.

if "pending_page" in st.session_state:
    st.session_state.page = st.session_state["pending_page"]
    del st.session_state["pending_page"]


# ---------- Styling ----------
CSS = """
<style>

/* Background */
.stApp {
    background: linear-gradient(180deg, #EDE7FB 0%, #F7F4FF 55%, #EFE9FD 100%);
    color: #1E1B4B;
}

[data-testid="stHeader"] {
    background: transparent;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B1464 0%, #2A1F7A 100%);
}

[data-testid="stSidebar"] * {
    color: #F4F1FF;
}

.side-brand {
    font-size: 1.35rem;
    font-weight: 800;
    color: #FFFFFF !important;
    margin-bottom: 4px;
}

/* Headings */
h1, h2, h3, h4 {
    color: #1E1B4B !important;
    font-weight: 700;
}

/* Body text */
p, li, span, label {
    color: #1E1B4B;
}

[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
    color: #1E1B4B !important;
    font-weight: 600;
}

[data-testid="stCaptionContainer"] p {
    color: #4B4670 !important;
}

/* Inputs */
.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background-color: #FFFFFF !important;
    color: #1E1B4B !important;
    border: 1px solid #CBB8F0 !important;
    border-radius: 12px !important;
    padding: 0.6rem 0.8rem;
}

.stTextInput input::placeholder,
.stNumberInput input::placeholder {
    color: #8A80A8;
    opacity: 1;
}

[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #1E1B4B !important;
    border: 1px solid #CBB8F0 !important;
    border-radius: 12px !important;
}

[data-baseweb="select"] span,
[data-baseweb="select"] div {
    color: #1E1B4B;
}

[role="listbox"] li,
[data-baseweb="menu"] li {
    background-color: #FFFFFF;
    color: #1E1B4B;
}

[role="listbox"] li:hover,
[data-baseweb="menu"] li:hover {
    background-color: #EDE7FB;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #6D3FD8, #8B5CF6);
    border: none;
    border-radius: 14px;
    padding: 0.7rem 1.2rem;
    font-weight: 700;
    width: 100%;
    box-shadow: 0 6px 16px rgba(109, 63, 216, 0.30);
}

.stButton > button,
.stButton > button p,
.stButton > button span,
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] .stButton > button p {
    color: #FFFFFF !important;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #5B2FC4, #7C3AED);
    color: #FFFFFF !important;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 14px;
}

[data-testid="stAlert"] p {
    color: #1E1B4B !important;
}

/* Streamlit metric cards */
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    padding: 16px;
    border-radius: 18px;
    border: 1px solid #E4DBF8;
    box-shadow: 0 4px 14px rgba(76, 29, 149, 0.08);
}

[data-testid="stMetricLabel"] p {
    color: #6D3FD8 !important;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #1E1B4B !important;
}

/* Progress bar */
[data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, #6D3FD8, #8B5CF6);
}

/* App bar (top navy banner like the mockups) */
.app-bar {
    background: linear-gradient(135deg, #1B1464 0%, #2E1E8A 100%);
    border-radius: 22px;
    padding: 16px 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;
    box-shadow: 0 8px 24px rgba(27, 20, 100, 0.25);
}

.app-bar .brand,
.app-bar .page-name {
    color: #FFFFFF !important;
    font-weight: 700;
    font-size: 1.05rem;
}

.app-bar .page-name {
    color: #D8CCFF !important;
    font-weight: 600;
}

/* Login hero card */
.hero {
    background: linear-gradient(160deg, #1B1464 0%, #3B1F9E 60%, #6D3FD8 100%);
    border-radius: 26px;
    padding: 28px 22px;
    text-align: center;
    margin-bottom: 18px;
    box-shadow: 0 10px 28px rgba(27, 20, 100, 0.3);
}

.hero .wallet {
    font-size: 3.6rem;
    margin-bottom: 6px;
}

.hero .hero-title {
    color: #FFFFFF !important;
    font-size: 1.7rem;
    font-weight: 800;
    margin: 0;
}

.hero .hero-sub {
    color: #E4DBFF !important;
    font-size: 0.98rem;
    margin: 4px 0 0 0;
}

/* Balance card */
.balance-card {
    background: linear-gradient(135deg, #2E1E8A 0%, #6D3FD8 100%);
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 14px;
    box-shadow: 0 8px 22px rgba(46, 30, 138, 0.3);
}

.balance-card .bc-label {
    color: #E4DBFF !important;
    font-size: 0.95rem;
    font-weight: 600;
    margin: 0;
}

.balance-card .bc-value {
    color: #FFFFFF !important;
    font-size: 2.1rem;
    font-weight: 800;
    margin: 6px 0;
}

.balance-card .bc-note {
    color: #CFF7E0 !important;
    font-size: 0.9rem;
    margin: 0;
}

/* Mini cards (income / expenses) */
.mini-card {
    background: #FFFFFF;
    border-radius: 18px;
    padding: 14px 16px;
    border: 1px solid #E4DBF8;
    box-shadow: 0 4px 14px rgba(76, 29, 149, 0.08);
}

.mini-card .mc-label {
    color: #4B4670 !important;
    font-weight: 600;
    margin: 0;
}

.mini-card .mc-value {
    color: #1E1B4B !important;
    font-size: 1.25rem;
    font-weight: 800;
    margin: 4px 0 0 0;
}

.up { color: #16A34A !important; }
.down { color: #DC2626 !important; }

/* Transaction rows */
.txn-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #FFFFFF;
    border-radius: 16px;
    padding: 12px 14px;
    margin-bottom: 10px;
    border: 1px solid #EFE9FD;
    box-shadow: 0 3px 10px rgba(76, 29, 149, 0.06);
}

.txn-left {
    display: flex;
    align-items: center;
}

.txn-icon {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    background: #EDE7FB;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    margin-right: 12px;
}

.txn-title {
    color: #1E1B4B !important;
    font-weight: 700;
    margin: 0;
}

.txn-date {
    color: #6B6592 !important;
    font-size: 0.85rem;
    margin: 0;
}

.txn-amount {
    font-weight: 800;
    font-size: 1rem;
}

.txn-amount.income { color: #16A34A !important; }
.txn-amount.expense { color: #DC2626 !important; }

/* Section label */
.section-title {
    color: #1E1B4B !important;
    font-weight: 700;
    font-size: 1.1rem;
    margin: 18px 0 8px 0;
}

/* Tip card */
.tip-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 14px 16px;
    border-left: 5px solid #6D3FD8;
    box-shadow: 0 4px 12px rgba(76, 29, 149, 0.08);
    margin-top: 12px;
}

.tip-card p {
    color: #1E1B4B !important;
    margin: 0;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------- Helper functions ----------
def app_bar(page_name):
    st.markdown(
        f'<div class="app-bar"><span class="brand">📊 SmartSpend</span>'
        f'<span class="page-name">{page_name}</span></div>',
        unsafe_allow_html=True
    )


def donut_chart(df, category_field, value_field):
    return (
        alt.Chart(df)
        .mark_arc(innerRadius=60, outerRadius=100)
        .encode(
            theta=alt.Theta(field=value_field, type="quantitative"),
            color=alt.Color(
                field=category_field,
                type="nominal",
                scale=alt.Scale(range=PALETTE),
                legend=alt.Legend(orient="right", labelColor="#1E1B4B", titleColor="#1E1B4B")
            ),
            tooltip=[category_field, value_field]
        )
        .properties(height=230)
    )


def transaction_row(t):
    icon = CATEGORY_ICONS.get(t["Category"], "💰")
    sign = "+" if t["Type"] == "Income" else "-"
    css_class = "income" if t["Type"] == "Income" else "expense"
    return (
        f'<div class="txn-row">'
        f'<div class="txn-left"><div class="txn-icon">{icon}</div>'
        f'<div><p class="txn-title">{t["Category"]}</p>'
        f'<p class="txn-date">{t["Description"]} · {t["Date"]}</p></div></div>'
        f'<div class="txn-amount {css_class}">{sign} ₹{t["Amount"]:,}</div>'
        f'</div>'
    )


# ---------- Sidebar navigation ----------
st.sidebar.markdown('<div class="side-brand">📊 SmartSpend</div>', unsafe_allow_html=True)
st.sidebar.write("Navigation Menu")

if st.session_state.logged_in:
    visible_pages = [
        "Dashboard",
        "Add Transaction",
        "History",
        "Budget",
        "Analysis"
    ]
else:
    visible_pages = ["Login", "Registration"]

page = st.sidebar.radio(
    "Select Page",
    visible_pages,
    key="page"
)

if not st.session_state.logged_in and page not in ["Login", "Registration"]:
    st.warning("Please login to access this page.")
    st.session_state.pending_page = "Login"
    st.rerun()

# Logout button (only visible when logged in)
if st.session_state.logged_in:
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.flash_message = "You have been logged out."
        st.session_state.pending_page = "Login"
        st.rerun()

# ---------- Top app bar (not on Login, which has its own hero) ----------
if page != "Login":
    app_bar(page)

# ---------- Pages ----------
if page == "Login":
    st.markdown(
        '<div class="hero">'
        '<div class="wallet">👛</div>'
        '<p class="hero-title">Welcome Back!</p>'
        '<p class="hero-sub">Track. Save. Grow.<br>Your personal finance tracker is here!</p>'
        '</div>',
        unsafe_allow_html=True
    )

    st.header("Login")

    # Show any message from a previous action (logout, registration)
    if st.session_state.flash_message:
        st.info(st.session_state.flash_message)
        st.session_state.flash_message = None

    if st.session_state.logged_in:
        st.info("You are already logged in.")

    email = st.text_input(
        "Email Address",
        placeholder="Enter your email"
    )

    password = st.text_input(
        "Password",
        placeholder="Enter your password",
        type="password"
    )

    if st.button("Login"):

        if not email.strip() or not password.strip():
            st.warning("Please enter both email and password!")

        elif email.count("@") != 1 or "." not in email.split("@")[-1] or " " in email:
            st.error("Please enter a valid email address.")

        else:
            # Successful login: mark user as logged in and go to Dashboard

            success, result = login_user(email, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user_id = result["user_id"]
                st.session_state.user_name = result["name"]
                st.session_state.pending_page = "Dashboard"

                st.rerun()
            else:
                st.error(result)

elif page == "Registration":
    st.header("Create Account")
    st.write("Join SmartSpend today!")

    name = st.text_input(
        "Full Name",
        placeholder="Enter your name"
    )

    email = st.text_input(
        "Email Address",
        placeholder="Enter your email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Create a password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Re-enter your password"
    )

    if st.button("Register"):

        if not name.strip() or not email.strip() or not password or not confirm_password:
            st.warning("Please fill all the fields!")

        elif password != confirm_password:
            st.error("Passwords do not match!")

        else:
            # Successful registration: show message and go to Login
            success, result = register_user(name, email, password)
            if success:
                st.session_state.flash_message = "Registration successful! Please log in."
                st.session_state.pending_page = "Login"
                st.rerun()
            else:
                st.error(result)


elif page == "Dashboard":
    st.header("Dashboard")
    st.write("Welcome back! Here's your financial snapshot.")

    # Fetch actual data from database
    success, totals = get_totals(st.session_state.user_id)
    if success:
        total_income = float(totals["total_income"])
        total_expenses = float(totals["total_expenses"])
        balance = float(totals["available_balance"])
    else:
        st.error(totals)
        total_income = 0
        total_expenses = 0
        balance = 0

    # Total balance card
    st.markdown(
        f'<div class="balance-card">'
        f'<p class="bc-label">Total Balance</p>'
        f'<p class="bc-value">₹{balance:,.2f}</p>'
        f'<p class="bc-note">▲ Income minus expenses</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Income and expense cards
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f'<div class="mini-card">'
            f'<p class="mc-label">🟢 Income</p>'
            f'<p class="mc-value up">₹{total_income:,.2f} ↑</p>'
            f'</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f'<div class="mini-card">'
            f'<p class="mc-label">🔴 Expenses</p>'
            f'<p class="mc-value down">₹{total_expenses:,.2f} ↓</p>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Spending overview chart
    st.markdown('<p class="section-title">Spending Overview</p>', unsafe_allow_html=True)

    # Fetch last 7 days transactions
    success, transactions = get_transactions(
        st.session_state.user_id
    )

    if success:
        spending_data = []

        today = date.today()
        start_date = today - timedelta(days=6)

        for t in transactions:
            tx_date = pd.to_datetime(
                t["transaction_date"]
            ).date()

            if (
                t["transaction_type"] == "Expense"
                and start_date <= tx_date <= today
            ):
                spending_data.append({
                    "Date": tx_date,
                    "Expenses": float(t["amount"])
                })

        if spending_data:
            spending_df = pd.DataFrame(spending_data)

            spending_df = spending_df.groupby(
                "Date", as_index=False
            )["Expenses"].sum()

            st.line_chart(
                spending_df,
                x="Date",
                y="Expenses"
            )
        else:
            st.info("No expenses in the last 7 days.")
    else:
        st.error(transactions)


elif page == "Add Transaction":
    st.header("Add Transaction")

    transaction_type = st.selectbox(
        "Transaction Type",
        ["Income", "Expense"]
    )

    amount = st.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=100.0
    )

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT category_id, category_name FROM categories")
    categories = cursor.fetchall()
    cursor.close()
    connection.close()

    category_options = {
        row["category_name"]: row["category_id"]
        for row in categories
    }

    category = st.selectbox(
        "Category",
        list(category_options.keys())
    )

    category_id = category_options[category]

    transaction_date = st.date_input("Transaction Date")

    description = st.text_input(
        "Description",
        placeholder="Enter transaction details"
    )

    if st.button("Add Transaction"):

        if amount <= 0:
            st.warning("Please enter a valid amount!")

        else:
            success, message = add_transaction(
                st.session_state.user_id,
                category_id,
                transaction_type,
                amount,
                description,
                transaction_date
            )

            if success:
                st.success(message)
            else:
                st.error(message)


elif page == "History":
    st.header("Transaction History")

    success, transactions = get_transactions(
        st.session_state.user_id
    )

    if not success:
        st.error(transactions)

    else:
        display_transactions = []

        for t in transactions:
            display_transactions.append({
                "Date": str(t["transaction_date"]),
                "ID": t["transaction_id"],
                "Category ID": t["category_id"],
                "Type": t["transaction_type"],
                "Category": t["category_name"],
                "Amount": float(t["amount"]),
                "Description": t["description"] or ""
            })

        st.markdown(
            '<p class="section-title">Filter Transactions</p>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            type_filter = st.selectbox(
                "Transaction Type",
                ["All", "Income", "Expense"]
            )

        categories = sorted(set(
            t["Category"] for t in display_transactions
        ))

        with col2:
            category_filter = st.selectbox(
                "Category",
                ["All"] + categories
            )

        filtered_transactions = display_transactions

        if type_filter != "All":
            filtered_transactions = [
                t for t in filtered_transactions
                if t["Type"] == type_filter
            ]

        if category_filter != "All":
            filtered_transactions = [
                t for t in filtered_transactions
                if t["Category"] == category_filter
            ]

        st.markdown(
            '<p class="section-title">All Transactions</p>',
            unsafe_allow_html=True
        )

        if filtered_transactions:
            for t in filtered_transactions:
                st.markdown(
                    transaction_row(t),
                    unsafe_allow_html=True
                )
        else:
            st.info("No transactions found.")

        with st.expander("Show as table"):
            st.dataframe(
                filtered_transactions,
                use_container_width=True
            )

        st.write(
            f"Total Transactions: {len(filtered_transactions)}"
        )

        st.markdown("---")
        st.subheader("Manage Transactions")

        if filtered_transactions:

            transaction_options = {
                f'{t["Category"]} - ₹{t["Amount"]} - {t["Date"]} (ID: {t["ID"]})': t
                for t in filtered_transactions
            }

            selected_transaction = st.selectbox(
                "Select a transaction",
                list(transaction_options.keys())
            )

            selected = transaction_options[selected_transaction]

            st.markdown("---")
            st.subheader("Edit Selected Transaction")

            edit_type = st.selectbox(
                "Transaction Type",
                ["Income", "Expense"],
                index=["Income", "Expense"].index(selected["Type"]),
                key="edit_type"
            )

            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                "SELECT category_id, category_name FROM categories"
            )

            edit_categories = cursor.fetchall()

            cursor.close()
            connection.close()

            edit_category_options = {
                row["category_name"]: row["category_id"]
                for row in edit_categories
            }

            category_names = list(edit_category_options.keys())

            current_category = next(
                name for name, category_id in edit_category_options.items()
                if category_id == selected["Category ID"]
            )

            edit_category = st.selectbox(
                "Category",
                category_names,
                index=category_names.index(current_category),
                key="edit_category"
            )

            edit_amount = st.number_input(
                "Amount (₹)",
                min_value=0.01,
                value=float(selected["Amount"]),
                key="edit_amount"
            )

            edit_date = st.date_input(
                "Transaction Date",
                value=pd.to_datetime(selected["Date"]).date(),
                key="edit_date"
            )

            edit_description = st.text_input(
                "Description",
                value=selected["Description"],
                key="edit_description"
            )

            if st.button("Update Transaction"):
                success, message = update_transaction(
                    selected["ID"],
                    st.session_state.user_id,
                    edit_category_options[edit_category],
                    edit_type,
                    edit_amount,
                    edit_description,
                    edit_date
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this transaction.",
                key="confirm_delete"
            )

            if st.button("Delete Transaction"):
                if confirm_delete:
                    success, message = delete_transaction(
                        selected["ID"],
                        st.session_state.user_id
                    )

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please confirm before deleting.")

        else:
            st.info("No transactions available to manage.")


elif page == "Budget":
    st.header("Monthly Budget")

    st.write("Set and track your monthly budget!")

    today = date.today()

    success, saved_budget = get_monthly_budget(
        st.session_state.user_id,
        today.month,
        today.year
    )

    if success:
        default_budget = saved_budget if saved_budget is not None else 20000.0
    else:
        st.error(saved_budget)
        default_budget = 20000.0

    monthly_budget = st.number_input(
        "Enter Your Monthly Budget (₹)",
        min_value=0.0,
        value=float(default_budget),
        step=1000.0
    )

    if st.button("Save Budget"):
        save_success, message = save_monthly_budget(
            st.session_state.user_id,
            monthly_budget,
            today.month,
            today.year
        )

        if save_success:
            st.success(message)
        else:
            st.error(message)

    # Fetch actual monthly expenses
    success, transactions = get_transactions(
        st.session_state.user_id
    )

    if success:
        today = date.today()
        total_expenses = 0.0

        for t in transactions:
            tx_date = pd.to_datetime(
                t["transaction_date"]
            ).date()

            if (
                t["transaction_type"] == "Expense"
                and tx_date.month == today.month
                and tx_date.year == today.year
            ):
                total_expenses += float(t["amount"])

        st.markdown(
            '<p class="section-title">Budget Overview</p>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Monthly Budget",
                f"₹{monthly_budget:,.2f}"
            )

        with col2:
            st.metric(
                "Total Expenses",
                f"₹{total_expenses:,.2f}"
            )

        if monthly_budget > 0:

            remaining = monthly_budget - total_expenses

            percentage = min(
                total_expenses / monthly_budget,
                1.0
            )

            st.markdown(
                '<p class="section-title">Budget Progress</p>',
                unsafe_allow_html=True
            )

            st.progress(percentage)

            st.write(
                f"₹{total_expenses:,.2f} spent ({percentage * 100:.1f}%)"
            )

            budget_df = pd.DataFrame({
                "Status": ["Spent", "Remaining"],
                "Amount": [total_expenses, max(remaining, 0.0)]
            })

            st.altair_chart(
                donut_chart(budget_df, "Status", "Amount"),
                use_container_width=True
            )

            if remaining >= 0:
                st.success(
                    f"Remaining Budget: ₹{remaining:,.2f}"
                )
            else:
                st.warning(
                    f"Budget Exceeded by ₹{abs(remaining):,.2f}"
                )

            st.markdown(
                '<div class="tip-card"><p>💡 You\'re on track! Keep going to meet your budget.</p></div>',
                unsafe_allow_html=True
            )

        else:
            st.warning("Please enter a budget greater than zero.")

    else:
        st.error(transactions)


elif page == "Analysis":

    st.header("Financial Analysis")
    st.write("Analyze your income and expenses!")

    # Fetch actual financial data
    # Fetch income and expense totals using analytics.py
    analysis_totals = get_income_expense_totals(
        st.session_state.user_id
    )

    if analysis_totals is not None:
        income = float(analysis_totals["total_income"])
        expenses = float(analysis_totals["total_expenses"])
    else:
        st.error("Unable to fetch financial analysis.")
        income = 0
        expenses = 0

    # Total spending card
    st.markdown(
        f'<div class="balance-card">'
        f'<p class="bc-label">Total Spending</p>'
        f'<p class="bc-value">₹{expenses:,.2f}</p>'
        f'<p class="bc-note">Based on your recorded transactions</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Income vs Expenses
    st.markdown(
        '<p class="section-title">Income vs Expenses</p>',
        unsafe_allow_html=True
    )

    comparison_data = {
        "Type": ["Income", "Expenses"],
        "Amount": [income, expenses]
    }

    st.bar_chart(
        comparison_data,
        x="Type",
        y="Amount"
    )

    # Monthly Expenses
    st.markdown(
        '<p class="section-title">Monthly Expenses</p>',
        unsafe_allow_html=True
    )

    monthly_df = get_monthly_totals(
        st.session_state.user_id
    )

    if monthly_df is not None and not monthly_df.empty:

        monthly_df["Period"] = (
            monthly_df["year"].astype(str)
            + "-"
            + monthly_df["month"].astype(str).str.zfill(2)
        )

        st.bar_chart(
            monthly_df,
            x="Period",
            y="total_expenses"
        )

    else:
        st.info("No monthly expense transactions available.")

    # Category-wise Expenses

    st.markdown(
        '<p class="section-title">Expense by Category</p>',
        unsafe_allow_html=True
    )

    category_df = get_category_totals(
        st.session_state.user_id
    )

    if category_df is not None and not category_df.empty:

        st.altair_chart(
            donut_chart(
                category_df,
                "category_name",
                "total_spent"
            ),
            use_container_width=True
        )

        st.bar_chart(
            category_df,
            x="category_name",
            y="total_spent"
        )

    else:
        st.info("No expense data available.")

    st.success("Financial analysis displayed successfully!")