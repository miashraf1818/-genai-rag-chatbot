# frontend/app.py
import streamlit as st
import asyncio
import websockets

st.title("🤖 GenAI RAG Chatbot")
st.caption("Ask questions about your Django documents!")

# User input
user_query = st.text_input("You:", placeholder="Ask me anything about Django...")

if st.button("Send") and user_query:
    with st.spinner("Thinking..."):
        response_placeholder = st.empty()


        # Connect to WebSocket and get response
        async def get_response():
            full_response = ""
            uri = "ws://localhost:8000/ws/chat"

            try:
                async with websockets.connect(uri) as websocket:
                    await websocket.send(user_query)

                    while True:
                        chunk = await websocket.recv()
                        if chunk == "[DONE]":
                            break
                        full_response += chunk
                        response_placeholder.markdown(f"**Bot:** {full_response}")

            except Exception as e:
                st.error(f"Error connecting to backend: {e}")


        asyncio.run(get_response())
