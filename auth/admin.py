import streamlit as st
from database.db import cursor


def admin_panel():
    st.title("Admin Panel")

    cursor.execute("SELECT username,email FROM users")

    users = cursor.fetchall()

    st.table(users)