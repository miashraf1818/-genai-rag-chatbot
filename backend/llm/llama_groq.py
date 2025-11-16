# backend/llm/llama_groq.py
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("your api key "))


def ask_llama_with_context(query: str, context: str):
    """
    Generate response using Llama 3 with retrieved context
    """
    prompt = f"""You are a helpful assistant. Use the following context to answer the user's question.

Context:
{context}

Question: {query}

Answer:"""

    # Stream response from Groq
    stream = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
