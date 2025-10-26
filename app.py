import streamlit as st
import pyrebase4 as pyrebase
import requests
import json
import webbrowser

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="🌍 Cross-Culture Humor Mapper", page_icon="😂", layout="centered")

# ---------------------------------------------------------
# FIREBASE CONFIG
# ---------------------------------------------------------
firebase_config = {
    "apiKey": st.secrets["firebase"]["apiKey"],
    "authDomain": st.secrets["firebase"]["authDomain"],
    "projectId": st.secrets["firebase"]["projectId"],
    "storageBucket": st.secrets["firebase"]["storageBucket"],
    "messagingSenderId": st.secrets["firebase"]["messagingSenderId"],
    "appId": st.secrets["firebase"]["appId"],
    "measurementId": st.secrets["firebase"]["measurementId"],
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception:
        st.error("❌ Invalid credentials or login failed.")
        return None

def signup_user(email, password):
    try:
        auth.create_user_with_email_and_password(email, password)
        st.success("✅ Account created! Please login now.")
    except Exception:
        st.error("⚠️ Could not create account. Try another email.")

def logout_user():
    st.session_state["user"] = None
    st.success("👋 Logged out successfully!")
    st.experimental_rerun()

# ---------------------------------------------------------
# UI STYLING
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #FFD6E8, #B5EAEA, #C7CEEA);
        color: #333;
        font-family: 'Poppins', sans-serif;
    }
    .login-box {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.2);
        width: 400px;
        margin: auto;
    }
    h1, h2 {
        text-align: center;
        color: #444;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOGIN / SIGNUP PAGE
# ---------------------------------------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.title("😂 Cross-Culture Humor Mapper")
    st.subheader("🌏 Translate humor across cultures and languages!")

    choice = st.radio("Choose", ["Login", "Sign Up"], horizontal=True)

    email = st.text_input("📧 Email")
    password = st.text_input("🔒 Password", type="password")

    if choice == "Login":
        if st.button("🚀 Login"):
            user = login_user(email, password)
            if user:
                st.session_state["user"] = user
                st.experimental_rerun()

    elif choice == "Sign Up":
        if st.button("✨ Create Account"):
            signup_user(email, password)

    st.write("---")
    st.markdown("### 🔑 Or Login with Google")

    google_login_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?client_id=" + st.secrets["firebase"]["apiKey"] +
        "&redirect_uri=https://your-app-name.streamlit.app"
        "&response_type=token&scope=email%20profile"
    )

    if st.button("🔵 Sign in with Google"):
        webbrowser.open(google_login_url)

    st.markdown("</div>", unsafe_allow_html=True)

else:
    # ---------------------------------------------------------
    # MAIN APP — After Login
    # ---------------------------------------------------------
    st.title("🌍 Cross-Culture Humor & Language Mapper")
    st.write("🎉 Welcome! Translate your jokes to make the world laugh together.")

    if st.button("Logout"):
        logout_user()

    source_culture = st.selectbox("🎭 Source Culture", ["American", "British", "Indian", "Japanese", "Other"])
    target_culture = st.selectbox("🎯 Target Culture", ["Indian", "American", "British", "Japanese", "Other"])
    target_language = st.selectbox(
        "🗣️ Translate into which language?",
        ["English", "Hindi", "Tamil", "Spanish", "French", "German", "Japanese"]
    )
    joke = st.text_area("💬 Enter your joke", placeholder="Type your joke here...")

    if st.button("🪄 Translate Humor"):
        if not joke:
            st.warning("Please enter a joke first!")
        else:
            with st.spinner("Translating... please wait ⏳"):
                try:
                    headers = {
                        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
                        "Content-Type": "application/json"
                    }

                    prompt = (
                        f"You are an expert in humor and cultural adaptation. "
                        f"Translate the following joke from {source_culture} culture to {target_culture} culture. "
                        f"Then express it in natural, funny {target_language}. "
                        f"Preserve humor and explain subtle cultural references if needed.\n\n"
                        f"Joke: {joke}"
                    )

                    data = {
                        "model": "mistralai/mistral-small-3.2-24b-instruct:free",
                        "messages": [
                            {"role": "system", "content": "You are a multilingual humor translator."},
                            {"role": "user", "content": prompt}
                        ]
                    }

                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        data=json.dumps(data)
                    )

                    if response.status_code == 200:
                        result = response.json()
                        output = result["choices"][0]["message"]["content"]
                        st.success(f"✅ Translated Joke in {target_language}:")
                        st.markdown(output)
                    elif response.status_code == 429:
                        st.error("⚠️ Rate limit reached. Try again later or add your own OpenRouter key.")
                    else:
                        st.error(f"❌ Error: {response.status_code}")
                        st.text(response.text)

                except Exception as e:
                    st.error(f"Unexpected error: {e}")
