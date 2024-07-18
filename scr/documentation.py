import streamlit as st
from PIL import Image
import os


def documentations():
    st.sidebar.image(Image.open(
        os.path.join(os.getcwd(),
                     "images",
                     "background.jpg"
                     )
                )
        )

    st.sidebar.markdown(
        "<div class='title'>CV Genius</div>", unsafe_allow_html=True
    )
    st.sidebar.markdown(
        "<div class='subtitle'>Améliorez votre processus de candidature</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        """<div class='description'>Cette application utilise des modèles d'IA
        pour vous aider à scorer votre CV, rédiger des lettres de motivation et
        améliorer votre CV.</div>""",
        unsafe_allow_html=True,
    )
    with st.sidebar.expander("Documentation", expanded=True):
        st.write("""Welcome to the documentation page for our project.
                 Here you will find all the necessary information to get
                 started with the Hugging Face API and Streamlit settings.
                 """)

        st.header("Hugging Face Access Key")
        st.write("""To use the Hugging Face API, you need to obtain an
                 access key. Follow these steps to get your key:""")
        st.markdown(
            """
            1. Go to the [Hugging Face website](https://huggingface.co/).
            """)
        st.markdown("""
                    2. Sign up for an account if you don't have one already.
                    """)
        st.markdown("3. Once logged in, go to your profile settings.")
        st.markdown("4. Look for the 'Access Tokens' section.")
        st.markdown("5. Generate a new access token and copy it.")
        st.markdown("""
                    <a href=https://huggingface.co/docs/hub/security-tokens>
                    For more information</a>""", unsafe_allow_html=True)

        st.header("Setting Hugging Face Access Key in Streamlit")
        st.write("""To use the Hugging Face API in your Streamlit app,
                 you need to set the access key as an environment
                 variable. Follow these steps:""")
        st.markdown("1. Open your application.")
        st.markdown("""2. At the bottom of your Streamlit app, click
                    on the manage app button, then select the 3 horizontal
                    dots, go to the settings, and select 'secrets' to
                    replace the new access key.""")

        # Load and display images
        doc1_path = os.path.join(os.getcwd(), "images", "doc1.png")
        doc1 = Image.open(doc1_path)
        st.image(doc1, caption="Manage app", use_column_width=True)

        doc2_path = os.path.join(os.getcwd(), "images", "doc2.png")
        doc2 = Image.open(doc2_path)
        st.image(doc2, caption="Manage app", use_column_width=True)

        st.write("""Now you can use the Hugging Face API in your
                 Streamlit app without any issues.""")
