import streamlit as st
from database.db import cursor
from auth.auth_utils import check_password


def login_user():
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        if user:
            stored_password = user[3]

            if check_password(password, stored_password):
                st.session_state.logged_in = True
                st.session_state.user = user[1]
                st.success("Login Successful")
            else:
                st.error("Wrong Password")
        else:
            st.error("User Not Found")