import streamlit as st
from database.db import conn, cursor
from auth.auth_utils import hash_password


def register_user():
    st.subheader("Register")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        hashed = hash_password(password)

        cursor.execute(
            "INSERT INTO users(username,email,password) VALUES(?,?,?)",
            (username, email, hashed)
        )

        conn.commit()

        st.success("Registration Successful")