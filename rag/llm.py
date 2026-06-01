from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_answer(query, context):

    prompt = f"""
You are an intelligent AI assistant.

Use context to answer clearly and simply.

Context:
{context}

Question:
{query}

Answer in simple explanation.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content