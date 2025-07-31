import streamlit as st
import pandas as pd
import sqlite3
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


CSV_FILE = "amazon-products.csv"
if not os.path.exists(CSV_FILE):
    st.error(f"❌ CSV file not found: {CSV_FILE}")
    st.stop()

#loading data 
df = pd.read_csv(CSV_FILE)

#loading sql agent 
conn = sqlite3.connect(":memory:")
df.to_sql("products", conn, index=False, if_exists="replace")

#model used 
model = genai.GenerativeModel("gemini-1.5-flash")


st.set_page_config(page_title="QueryMind", page_icon="🧠")
st.title("🧠 QueryMind")
st.markdown("Ask anything related to the product dataset below:")


user_input = st.text_input("💬 Enter your question in English:")

if user_input:
    prompt = f"""
You are an expert data assistant working with a SQLite table called 'products'.
The table contains the following columns: {', '.join(df.columns)}.

Convert the following natural language question into a correct SQL SELECT query.
Only return the SQL query (no explanations, no markdown formatting).

User question: {user_input}
"""

    try:
        response = model.generate_content(prompt)
        sql_query = response.text.strip().replace("```sql", "").replace("```", "").strip()

        st.markdown("📄 **Generated SQL Query**")
        st.code(sql_query, language="sql")

        try:
            result = pd.read_sql_query(sql_query, conn)
            st.markdown("📊 **Query Result**")
            st.dataframe(result)
        except Exception as sql_error:
            st.error(f"❌ SQL Execution Error:\n{sql_error}")

    except Exception as e:
        st.error(f"❌ Gemini API Error:\n{e}")