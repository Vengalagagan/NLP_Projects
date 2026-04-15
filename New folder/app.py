import streamlit as st
import pickle
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="Student Feedback Analytics", layout="wide")

# ============================================================
# LOGIN CREDENTIALS
# ============================================================
USER_CREDENTIALS = {
    "admin": "admin123",
    "dr_rao": "rao123",
    "dr_mehta": "mehta123",
    "dr_sharma": "sharma123",
    "student": "student123",
}

# ============================================================
# SESSION STATE
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

# ============================================================
# LOAD MODEL
# ============================================================
@st.cache_resource
def load_model():
    with open("sentiment_model.pkl", "rb") as file:
        return pickle.load(file)

model = load_model()

# ============================================================
# LOGIN PAGE
# ============================================================
if not st.session_state.logged_in:
    st.title("🔐 Student Feedback Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.role = username
            st.success("✅ Login successful")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

    st.stop()

role = st.session_state.role

# ============================================================
# MAIN DASHBOARD
# ============================================================
st.title("🎓 Student Feedback Analytics Dashboard")
st.write(f"Logged in as: **{role}**")
st.divider()

# ============================================================
# STUDENT SECTION
# ============================================================
if role == "student":
    st.subheader("📝 Submit Feedback")

    faculty = st.text_input("Faculty Name")
    subject = st.text_input("Subject")
    feedback = st.text_area("Enter your feedback")

    if st.button("Submit Feedback"):
        cleaned_feedback = feedback.strip().lower()

        if cleaned_feedback == "":
            st.warning("Please enter feedback")
        else:
            prediction = model.predict([cleaned_feedback])[0]

            # Save submitted feedback into CSV
            new_data = pd.DataFrame({
                "feedback": [cleaned_feedback],
                "sentiment": [prediction],
                "subject": [subject],
                "faculty": [faculty]
            })

            file_name = "feedback_dataset.csv"

            if os.path.exists(file_name):
                existing_df = pd.read_csv(file_name)
                updated_df = pd.concat([existing_df, new_data], ignore_index=True)
                updated_df.to_csv(file_name, index=False)
            else:
                new_data.to_csv(file_name, index=False)

            st.success("✅ Feedback submitted successfully")
            st.write("### Predicted Sentiment:", prediction)

# ============================================================
# ADMIN / FACULTY ANALYTICS
# ============================================================
if role in ["admin", "dr_rao", "dr_mehta", "dr_sharma"]:
    st.subheader("📊 Feedback Analytics")

    file_name = "feedback_dataset.csv"

    if not os.path.exists(file_name):
        st.error("❌ feedback_dataset.csv not found")
        st.stop()

    df = pd.read_csv(file_name)
    df.columns = df.columns.str.lower().str.strip()

    required_cols = ["feedback", "faculty", "subject", "sentiment"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Missing column: {col}")
            st.stop()

    # Clean data
    df["feedback"] = df["feedback"].fillna("").astype(str).str.strip().str.lower()
    df["faculty"] = df["faculty"].fillna("").astype(str).str.strip().str.lower()
    df["subject"] = df["subject"].fillna("").astype(str).str.strip()
    df["sentiment"] = df["sentiment"].fillna("").astype(str).str.strip().str.lower()

    df = df[df["feedback"] != ""]

    # ========================================================
    # FACULTY FILTERING
    # ========================================================
    if role == "dr_rao":
        df = df[df["faculty"].str.contains("rao", case=False)]

    elif role == "dr_mehta":
        df = df[df["faculty"].str.contains("mehta", case=False)]

    elif role == "dr_sharma":
        df = df[df["faculty"].str.contains("sharma", case=False)]

    # ========================================================
    # METRICS
    # ========================================================
    total = len(df)
    positive = len(df[df["sentiment"] == "positive"])
    negative = len(df[df["sentiment"] == "negative"])
    neutral = len(df[df["sentiment"] == "neutral"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", total)
    c2.metric("Positive", positive)
    c3.metric("Negative", negative)
    c4.metric("Neutral", neutral)

    st.divider()

    # ========================================================
    # FACULTY CHART
    # ========================================================
    faculty_chart = (
        df.groupby(["faculty", "sentiment"])
        .size()
        .reset_index(name="Count")
    )

    fig_fac = px.bar(
        faculty_chart,
        x="faculty",
        y="Count",
        color="sentiment",
        barmode="group",
        title="Faculty-wise Sentiment Analysis"
    )
    st.plotly_chart(fig_fac, use_container_width=True)

    # ========================================================
    # SUBJECT CHART
    # ========================================================
    subject_chart = (
        df.groupby(["subject", "sentiment"])
        .size()
        .reset_index(name="Count")
    )

    fig_sub = px.bar(
        subject_chart,
        x="subject",
        y="Count",
        color="sentiment",
        barmode="group",
        title="Subject-wise Sentiment Analysis"
    )
    st.plotly_chart(fig_sub, use_container_width=True)

    # ========================================================
    # PIE CHART
    # ========================================================
    pie_data = df["sentiment"].value_counts().reset_index()
    pie_data.columns = ["Sentiment", "Count"]

    fig_pie = px.pie(
        pie_data,
        values="Count",
        names="Sentiment",
        title="Overall Sentiment Distribution"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # =======================================================
    # WORD CLOUD
    # =======================================================
    st.subheader("☁️ Feedback Word Cloud")

    text = " ".join(df["feedback"])

    wc = WordCloud(
        width=1000,
        height=400,
        background_color="white"
    ).generate(text)

    fig_wc, ax = plt.subplots(figsize=(12, 4))
    ax.imshow(wc)
    ax.axis("off")
    st.pyplot(fig_wc)