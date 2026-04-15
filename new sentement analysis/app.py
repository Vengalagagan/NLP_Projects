import streamlit as st
import pandas as pd
import base64
from database import *
from sentiment import analyze_sentiment
from auth import login

# =========================
# DATABASE INIT
# =========================
create_tables()

# =========================
# BACKGROUND FUNCTION
# =========================
def set_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        .glass {{
            background: rgba(255,255,255,0.85);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# =========================
# SESSION STATE
# =========================
if "page" not in st.session_state:
    st.session_state["page"] = "home"

# =========================
# LOGIN PAGE
# =========================
if "role" not in st.session_state:
    set_bg("bg.png")

    st.title("🎓 University Feedback System")
    st.markdown("## Select Login Type")

    col1, col2, col3 = st.columns(3)

    if col1.button("🎓 Student"):
        st.session_state["login_role"] = "student"

    if col2.button("👨‍🏫 Teacher"):
        st.session_state["login_role"] = "teacher"

    if col3.button("🛠 Admin"):
        st.session_state["login_role"] = "admin"

    if "login_role" in st.session_state:
        login()

    st.stop()

# =========================
# USER DETAILS
# =========================
role = st.session_state["role"]
user = st.session_state["user"]

st.sidebar.write(f"Logged in as: {user} ({role})")

# =========================
# LOGOUT
# =========================
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# =====================================================
# STUDENT
# =====================================================
if role == "student":

    # ---------- Dynamic Background ----------
    if st.session_state.get("page") == "feedback":
        set_bg("feedback_bg.png")
    else:
        set_bg("student_bg.png")

    st.header("📘 Give Feedback")

    courses = [
        {"faculty": "VENKATARAMANA V", "course": "NLP"},
        {"faculty": "SHENDE AMIT", "course": "Smart Farming"},
        {"faculty": "PRAVEEN", "course": "Data Structures"},
    ]

    # ---------- Student Home ----------
    if st.session_state.get("page") == "home":
        for c in courses:
            col1, col2, col3 = st.columns([3, 4, 2])

            col1.write(c["faculty"])
            col2.write(c["course"])

            if col3.button("Give Feedback", key=c["course"]):
                st.session_state["selected"] = c
                st.session_state["page"] = "feedback"
                st.rerun()

    # ---------- Feedback Page ----------
    if st.session_state.get("page") == "feedback" and "selected" in st.session_state:

        c = st.session_state["selected"]

        st.subheader(f"✍️ Feedback for {c['faculty']}")

        fb_key = f"fb_{c['faculty']}"
        rt_key = f"rt_{c['faculty']}"

        if st.button("🔄 Clear Form"):
            st.session_state[fb_key] = ""
            st.session_state[rt_key] = 3
            st.rerun()

        if fb_key not in st.session_state:
            st.session_state[fb_key] = ""

        if rt_key not in st.session_state:
            st.session_state[rt_key] = 3

        feedback_text = st.text_area("Enter feedback", key=fb_key)
        rating = st.slider("Rate Faculty", 1, 5, key=rt_key)

        if st.button("Submit Feedback"):

            sentiment = analyze_sentiment(feedback_text)

            save_feedback(
                user,
                c["faculty"],
                c["course"],
                feedback_text,
                sentiment,
                rating
            )

            st.success("✅ Feedback Submitted Successfully!")

            if sentiment == "Good 😊":
                st.success("🟢 Positive Feedback")
                st.balloons()
            elif sentiment == "Bad 😠":
                st.error("🔴 Negative Feedback")
            else:
                st.warning("🟡 Neutral Feedback")

            st.session_state.pop(fb_key, None)
            st.session_state.pop(rt_key, None)
            st.session_state.pop("selected", None)

            st.session_state["page"] = "home"
            st.rerun()

# =====================================================
# TEACHER
# =====================================================
elif role == "teacher":
    set_bg("teacher_bg.png")

    st.header("📊 Your Feedback Dashboard")

    data = get_teacher_feedback(user)
    df = pd.DataFrame(
        data,
        columns=["id", "student", "faculty", "course", "feedback", "sentiment", "rating"]
    )

    if not df.empty:
        st.metric("⭐ Average Rating", round(df["rating"].mean(), 2))

        st.subheader("⭐ Rating Distribution")
        st.bar_chart(df["rating"].value_counts())

        st.subheader("📝 Student Feedback")

        for _, row in df.iterrows():
            st.markdown(
                f"""
                <div class="glass">
                    <b>📘 Course:</b> {row['course']} <br>
                    <b>💬 Feedback:</b> {row['feedback']} <br>
                    <b>😊 Sentiment:</b> {row['sentiment']} | ⭐ {row['rating']}
                </div>
                <br>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No feedback yet")

# =====================================================
# ADMIN
# =====================================================
elif role == "admin":
    set_bg("admin_bg.png")

    st.header("📊 Admin Analytics Dashboard")

    data = get_all_feedback()
    df = pd.DataFrame(
        data,
        columns=["id", "student", "faculty", "course", "feedback", "sentiment", "rating"]
    )

    if not df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("😊 Sentiment Analysis")
            st.bar_chart(df["sentiment"].value_counts())

        with col2:
            st.subheader("⭐ Rating Distribution")
            st.bar_chart(df["rating"].value_counts())

        st.subheader("👨‍🏫 Faculty Performance")
        st.bar_chart(df.groupby("faculty")["rating"].mean())

        st.subheader("📋 Full Data")
        st.dataframe(df)

    else:
        st.info("No data available")