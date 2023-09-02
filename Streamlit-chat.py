import streamlit as st
import os
import json
import re
import pandas as pd
from streamlit_chat import message
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

def init():
    load_dotenv()
    #Load API key from .env
    if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
        print("Open AI key is not set")
        exit(1)
    else:
        print("Open AI key is set")

    st.set_page_config(
        page_title = "Flight Booking Assistant"
    )
    

def main():
    init()

    chat = ChatOpenAI(temperature = 0)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content="""The following is a conversation with an AI assistant. If the user wants they can talk about anything as soon as the assistant finishes collecting the following fields from the user:
                The user's name
                The user's email
                The user's departure location
                The user's destination location
                The user's dates of travel
                The user's budget for the trip

                After collecting all these fields the AI should thank the human for their time and tell them they'll recieve email. 
                It should then write EODC (for end of data collection) and on a new line output all these fields as JSON. {"user_name": "<user_name>", "user_email": "<user_email>", "departure_location": <departure_location>, "destination_location": "<destination_location>", "departure_date": "departure_date", "return_date":"return_date", "budget": "<budget>"}
                AI: Hi! I can help you book a flight. Can I start by getting your name?
            """),
        ]

    st.header("Booking a Flight")

    with st.sidebar:
        user_input = st.text_input("Your Message: ", key="user inputcl")
    
    if user_input:
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.spinner("Writing.."):
            response = chat(st.session_state.messages)
            if "EODC" in response.content:
                response.content = response.content.split("EODC")[0].strip()
        st.session_state.messages.append(AIMessage(content=response.content))

    messages = st.session_state.get("messages", [])
    for i, msg in enumerate(messages[1:]):
        if i % 2 == 0:
            message(msg.content, is_user=True, key=str(i)+"_user")
        else: message(msg.content, is_user=False, key=str(i)+"_ai")
    
     
    if "EODC" in messages[-1].content:
        data = messages[-1].content.split("EODC")[1]
        data = data.strip().replace("{", "").replace("}", "")
        # Define a regex pattern to match key-value pairs
        pattern = r'"(\w+)": "(.*?)"'

        # Use regex to find all matches
        matches = re.findall(pattern, data)

        # Create a dictionary from the matches
        info_dict = {key: value for key, value in matches}
    
    print(info_dict)

if __name__ == "__main__":
    main()