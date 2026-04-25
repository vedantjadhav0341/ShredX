import streamlit as st
from groq import Groq
import pandas as pd
from datetime import date
import random

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="ShredX", page_icon="💎", layout="wide")

# ---------------- API ---------------- #
import os
API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)
# ---------------- CSS ---------------- #
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef2f7, #d9e4f5);
    font-family: 'Segoe UI', sans-serif;
}
.main-container {
    max-width: 500px;
    margin: auto;
}
.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
div.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2);
    color: white;
    border-radius: 10px;
    height: 45px;
    border: none;
}
.title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: bold;
}
.subtitle {
    text-align: center;
    color: #555;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if "users" not in st.session_state:
    st.session_state.users = {}  # username: password

if "messages" not in st.session_state:
    st.session_state.messages = []

if "progress" not in st.session_state:
    st.session_state.progress = []

# ================= AUTH PAGES ================= #
if not st.session_state.logged_in:

    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    st.markdown("<div class='title'>💎 ShredX</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Your AI Fitness Coach</div>", unsafe_allow_html=True)

    # -------- REGISTER -------- #
    if st.session_state.page == "register":
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📝 Register")

        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Create Account"):
            if new_user in st.session_state.users:
                st.error("User already exists")
            elif new_user == "" or new_pass == "":
                st.error("Fill all fields")
            else:
                st.session_state.users[new_user] = new_pass
                st.success("Account created! Please login.")
                st.session_state.page = "login"

        if st.button("Go to Login"):
            st.session_state.page = "login"

        st.markdown("</div>", unsafe_allow_html=True)

    # -------- LOGIN -------- #
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🔐 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")

        if st.button("Create New Account"):
            st.session_state.page = "register"

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ================= MAIN APP ================= #
else:

    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    st.markdown("<div class='title'>ShredX</div>", unsafe_allow_html=True)

    quotes = [
        "Consistency beats motivation",
        "Train smart, not just hard",
        "Discipline builds results",
    ]
    st.markdown(f"<div class='subtitle'>{random.choice(quotes)}</div>", unsafe_allow_html=True)

    # PROFILE
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🏋️ Profile")

    weight = st.number_input("Weight", 40, 150, 80)
    height = st.number_input("Height", 140, 210, 170)
    goal = st.selectbox("Goal", ["Cutting", "Bulking", "Maintain"])

    st.markdown("</div>", unsafe_allow_html=True)

    # MACROS
    if goal == "Cutting":
        calories = weight * 25
    elif goal == "Bulking":
        calories = weight * 35
    else:
        calories = weight * 30

    protein = weight * 2
    fats = weight * 0.8
    carbs = int((calories - (protein*4 + fats*9)) / 4)

    # DASHBOARD
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📊 Dashboard")

    st.metric("Calories", calories)
    st.metric("Protein", protein)
    st.metric("Carbs", carbs)
    st.metric("Fats", fats)

    st.markdown("</div>", unsafe_allow_html=True)

    # CHAT
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("💬 Coach")

    system_prompt = f"""
    You are ShredX fitness coach.

    Weight: {weight}
    Goal: {goal}

    Give workout, diet, motivation.
    """

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    text = st.chat_input("Ask ShredX...")

    if text:
        st.session_state.messages.append({"role": "user", "content": text})

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages
            )
            reply = response.choices[0].message.content
        except:
            reply = "Error occurred"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # PROGRESS
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📈 Progress")

    new_weight = st.number_input("Update Weight", 40, 150, weight)

    if st.button("Save Progress"):
        st.session_state.progress.append({"date": str(date.today()), "weight": new_weight})

    if st.session_state.progress:
        df = pd.DataFrame(st.session_state.progress)
        st.line_chart(df.set_index("date"))

    st.markdown("</div>", unsafe_allow_html=True)

    # LOGOUT
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
