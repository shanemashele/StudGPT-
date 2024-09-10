import streamlit as st
import os
import hashlib
import csv
from dotenv import load_dotenv
import time
from groq import Groq

# Load environment variables
load_dotenv()

USERS_FILE = 'users.csv'

def hash_password(password):
    """Hash the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, name, surname, email):
    """Register a new user by appending their details to the CSV file."""
    hashed_password = hash_password(password)
    with open(USERS_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, hashed_password, name, surname, email])

def login_user(username, password):
    """Authenticate a user by checking username and password."""
    hashed_password = hash_password(password)
    with open(USERS_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username and row[1] == hashed_password:
                return True
    return False

def user_exists(username):
    """Check if a username already exists in the CSV file."""
    with open(USERS_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username:
                return True
    return False

def get_user_info(username):
    """Retrieve user information from the CSV file based on the username."""
    with open(USERS_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username:
                return {
                    'name': row[2],
                    'surname': row[3],
                    'email': row[4]
                }
    return None

def create_users_file():
    """Create the users CSV file with headers if it does not exist."""
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'password', 'name', 'surname', 'email'])

# Load Groq API key
GROQ_API_KEY='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'
client = Groq(api_key=GROQ_API_KEY)

# Set page configuration
st.set_page_config(page_title="StudGPT", page_icon="pic.png")

# Create users file if it doesn't exist
create_users_file()

# User session state to track login status and user info
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'name' not in st.session_state:
    st.session_state.name = ''
if 'surname' not in st.session_state:
    st.session_state.surname = ''
if 'email' not in st.session_state:
    st.session_state.email = ''
if 'profile_picture' not in st.session_state:
    st.session_state.profile_picture = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Registration and Login
if not st.session_state.logged_in:
    st.sidebar.title("User Authentication")

    # Registration
    with st.sidebar.expander("Register"):
        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_name = st.text_input("Name", key="reg_name")
        reg_surname = st.text_input("Surname", key="reg_surname")
        reg_email = st.text_input("Email", key="reg_email")
        if st.button("Register"):
            if not user_exists(reg_username):
                register_user(reg_username, reg_password, reg_name, reg_surname, reg_email)
                st.success("User registered successfully.")
            else:
                st.error("Username already exists.")

    # Login
    with st.sidebar.expander("Login"):
        log_username = st.text_input("Username", key="log_username")
        log_password = st.text_input("Password", type="password", key="log_password")
        if st.button("Login"):
            if login_user(log_username, log_password):
                st.session_state.logged_in = True
                st.session_state.username = log_username
                user_info = get_user_info(log_username)  # Fetch the user's info
                st.session_state.name = user_info['name'].capitalize()
                st.session_state.surname = user_info['surname'].capitalize()
                st.session_state.email = user_info['email']
                st.success("Logged in successfully.")
            else:
                st.error("Invalid username or password.")

if st.session_state.logged_in:
    st.sidebar.title(f"Welcome, {st.session_state.name} {st.session_state.surname}")

    # User Information Section
    with st.sidebar.expander("Your Information"):
        st.write(f"**Name:** {st.session_state.name} {st.session_state.surname}")
        st.write(f"**Email:** {st.session_state.email}")
        if st.session_state.profile_picture:
            st.image(st.session_state.profile_picture, caption="Profile Picture", use_column_width=True)

    # Update Profile
    with st.sidebar.expander("Update Profile"):
        new_name = st.text_input("New Name", value=st.session_state.name, key="new_name")
        new_email = st.text_input("New Email", value=st.session_state.email, key="new_email")
        new_password = st.text_input("New Password", type="password", key="new_password")
        if st.button("Update Profile"):
            # Update the user profile in the CSV file
            # Here you need to implement a method to update user details in the CSV
            st.session_state.name = new_name
            st.session_state.email = new_email
            st.success("Profile updated successfully.")

    

    # Chat Interface
    st.title("Student World")
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if question := st.chat_input(placeholder="Ask Me"):
        st.session_state.chat_history.append({"role": "user", "content": question})

        # Display user's message
        with st.chat_message("user"):
            st.markdown(question)

        # Create chat completion request
        start = time.process_time()
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": "You are a helpful assistant."}] + st.session_state.chat_history,
            model="llama3-8b-8192",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )
        response_time = time.process_time() - start

        answer = chat_completion.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

        # Display assistant's response
        with st.chat_message("assistant"):
            st.markdown(answer)

    # Logout
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.name = ''
        st.session_state.surname = ''
        st.session_state.email = ''
        st.session_state.profile_picture = None
        st.session_state.chat_history = []
        st.success("Logged out successfully.")

else:
    st.title("Welcome To The MultiUniverse Answer")
    st.write("Please log in to interact with the chatbot.")
    st.image(image="pic.png", use_column_width=True)
    st.write("The mission of this app is to provide users with a secure and personalized experience to access advanced AI-driven assistance.")
    st.write("By ensuring that users register and log in, the app aims to create a safe and tailored environment where individuals can engage with a powerful language model to receive accurate, reliable, and insightful answers to their questions, enhancing their knowledge and problem-solving capabilities.")
