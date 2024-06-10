import streamlit as st
from PIL import Image
import os


def documentations():
    st.title("Documentation")
    # st.write("Welcome to the documentation page for our project. Here you will find all the necessary information to huggingface acces key and setting in streamlit.")
    st.header("Hugging Face Access Key")
    st.write("To use the Hugging Face API, you need to obtain an access key. Follow these steps to get your key:")
    st.markdown("1. Go to the [Hugging Face website](https://huggingface.co/).")
    st.markdown("2. Sign up for an account if you don't have one already.")
    st.markdown("3. Once logged in, go to your profile settings.")
    st.markdown("4. Look for the 'Access Tokens' section.")
    st.markdown("5. Generate a new access token and copy it.")
    st.markdown("<a href=https://huggingface.co/docs/hub/security-tokens> For informations </a>", unsafe_allow_html=True)
    st.header("Setting Hugging Face Access Key in Streamlit")
    st.write("To use the Hugging Face API in your Streamlit app, you need to set the access key as an environment variable. Follow these steps:")
    st.markdown("1. Open your application")
    st.markdown("2. At the bottom of your Streamlit app, click on manage app button and then select the 3 horizontal dots and then go to the settings and select now secrets to remplace the new acces key")
    doc1_path = os.path.join(os.getcwd(), "images", "doc1.png")
    doc1 = Image.open(doc1_path)
    st.image(doc1, caption="Manage app", use_column_width=True)
    doc2_path = os.path.join(os.getcwd(), "images", "doc2.png")
    doc2 = Image.open(doc2_path)
    st.image(doc2, caption="Manage app", use_column_width=True)
    st.write("Now you can use the Hugging Face API in your Streamlit app without any issues.")
    