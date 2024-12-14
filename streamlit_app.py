import streamlit as st
from openai import OpenAI
from typing import Generator


st.set_page_config(page_icon="👨‍💼", layout="wide",
                   page_title="Mee Mee's Resume Bot")


st.subheader("👨‍💼📊📈📁 Mee Mee's Interactive Resume")
st.write(
    "Welcome to Mee Mee's personal chat bot to answer John's previous experiences and his skillsets. Ask away what you want to know!"
)

client = OpenAI(
    api_key=st.secrets["XAI_API_KEY"],
    base_url="https://api.x.ai/v1",
)

with open('assets/prompt.txt') as f:
    prompt = f.readlines()

with open('assets/resume.txt') as f:
    resume = f.readlines()

# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = []

system_prompt = {"role": "system", "content": f"""{prompt} \n <document> \n {resume} \n </document> """}

st.session_state["messages"].append(system_prompt)

if "model" not in st.session_state:
    st.session_state.model = "grok-beta"


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = '🤖' if message["role"] == "assistant" else '👨‍💻'
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


if prompt := st.chat_input("Ask what you want to know about John's resume..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar='👨‍💻'):
        st.markdown(prompt)

    try:
        chat_completion = client.chat.completions.create(
            model=st.session_state.model,
            messages=[
                {
                    "role": m["role"],
                    "content": m["content"]
                }
                for m in st.session_state.messages
            ],
            stream=True
        )

        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="🤖"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
    except Exception as e:
        st.error(e, icon="🚨")

    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
    else:
        # Handle the case where full_response is not a string
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response})