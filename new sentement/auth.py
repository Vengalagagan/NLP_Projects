import streamlit as st
from database import login_user

def login():
    st.subheader(f"{st.session_state['login_role'].capitalize()} Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(username, password)

        if user and user[2] == st.session_state["login_role"]:
            st.session_state["user"] = user[0]
            st.session_state["role"] = user[2]
            st.success("Login Successful")
        else:
            st.error("Invalid credentials or wrong role")
