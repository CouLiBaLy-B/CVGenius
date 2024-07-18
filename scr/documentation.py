import streamlit as st
from PIL import Image
import os


def documentations():
    st.sidebar.title("Documentation")
    # st.write("Welcome to the documentation page for our project. Here you
    # will find all the necessary information to huggingface acces key
    # and setting in streamlit.")
    st.sidebar.header("Hugging Face Access Key")
    st.sidebar.write("""To use the Hugging Face API, you need to obtain an
                     access key. Follow these steps to get your key:""")
    st.sidebar.markdown("""1. Go to the [Hugging Face website]
                (https://huggingface.co/).""")
    st.sidebar.markdown("""2. Sign up for an account if you don't have
                        one already.""")
    st.sidebar.markdown("3. Once logged in, go to your profile settings.")
    st.sidebar.markdown("4. Look for the 'Access Tokens' section.")
    st.sidebar.markdown("5. Generate a new access token and copy it.")
    st.sidebar.markdown(
        """<a href=https://huggingface.co/docs/hub/security-tokens>
        For informations </a>""",
        unsafe_allow_html=True)
    st.sidebar.header("Setting Hugging Face Access Key in Streamlit")
    st.sidebar.write("""To use the Hugging Face API in your Streamlit app,
                     you need to set the access key as an environment
                     variable. Follow these steps:""")
    st.sidebar.markdown("1. Open your application")
    st.sidebar.markdown("""2. At the bottom of your Streamlit app, click on
                        manage app button and then select the 3 horizontal
                        dots and then go to the settings and select now
                        secrets to remplace the new acces key""")
    doc1_path = os.path.join(os.getcwd(), "images", "doc1.png")
    doc1 = Image.open(doc1_path)
    st.sidebar.image(doc1, caption="Manage app", use_column_width=True)
    doc2_path = os.path.join(os.getcwd(), "images", "doc2.png")
    doc2 = Image.open(doc2_path)
    st.sidebar.image(doc2, caption="Manage app", use_column_width=True)
    st.sidebar.write("""Now you can use the Hugging Face API in your Streamlit
                     app without any issues.""")
