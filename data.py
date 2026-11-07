import mysql.connector
import streamlit as st

def get_connection():
    connection = mysql.connector.connect(
        host=st.secrets["tidb"]["host"],
        port=st.secrets["tidb"]["port"],
        user=st.secrets["tidb"]["user"],
        password=st.secrets["tidb"]["password"],
        database=st.secrets["tidb"]["database"],
        ssl_ca="ca.pem",
        ssl_verify_cert=True,
        ssl_verify_identity=True,
        connection_timeout=10
    )
    return connection