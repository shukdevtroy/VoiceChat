import streamlit as st
import pandas as pd
import openai
from text_speech_utils import *  # Assuming this module exists for your audio functionality

# Define filenames for audio and conversation output
input_audio_filename = 'input.wav'
output_audio_filename = 'chatgpt_response.wav'
output_conversation_filename = 'ChatGPT_conversation.txt'

# Initialize app
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{"role": "system", "content": "You are a helpful assistant."}]

# Allow user to input OpenAI API Key via Streamlit text input
openai.api_key = st.text_input("Enter your OpenAI API Key", type="password")

# Display a warning if API key is not provided
if not openai.api_key:
    st.warning("Please enter your OpenAI API key to proceed.")

# UI components
st.title("My awesome personal assistant")
sec = st.slider("Select number of seconds of recording", min_value=2, max_value=8, value=5)

# Record audio + transcribe with Whisper + get GPT-3 response
if st.button('Record audio'):
    if openai.api_key:  # Proceed only if API key is provided
        st.write("Recording...")
        record_audio(input_audio_filename, sec)

        transcription = transcribe_audio(input_audio_filename)
        st.write(f"Me: {transcription['text']}")
        st.session_state['messages'].append({"role": "user", "content": transcription['text']})

        bot = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state['messages'])
        response = bot.choices[0].message.content
        st.write(f"GPT: {response}")

        save_text_as_audio(response, output_audio_filename)
        play_audio(output_audio_filename)

        st.session_state['messages'].append({"role": "assistant", "content": response})
    else:
        st.error("API key is required to interact with GPT.")

# # Download conversation button
# st.download_button(label="Download conversation", 
#                    data=pd.DataFrame(st.session_state['messages']).to_csv(index=False).encode('utf-8'), 
#                    file_name=output_conversation_filename)

# Function to generate conversation as plain text
def generate_conversation_text(messages):
    conversation_text = ""
    for message in messages:
        if message["role"] == "user":
            conversation_text += f"Me: {message['content']}\n"
        elif message["role"] == "assistant":
            conversation_text += f"GPT: {message['content']}\n"
        elif message["role"] == "system":
            conversation_text += f"System: {message['content']}\n"
    return conversation_text

# Download conversation button
st.download_button(
    label="Download conversation", 
    data=generate_conversation_text(st.session_state['messages']).encode('utf-8'), 
    file_name=output_conversation_filename,
    mime="text/plain"
)