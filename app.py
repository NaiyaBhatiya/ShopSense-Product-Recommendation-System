import streamlit as st
import pandas as pd
import os
from ShopSense import recommend_products
from streamlit_option_menu import option_menu


def load_users():
    return pd.read_csv("user.csv")


def check_login(email, password, users_df):
    user = users_df[(users_df['email'] == email) & (users_df['password'] == password)]
    return not user.empty


def register_user(email, password):
    try:
        if os.path.exists("user.csv"):
            users = pd.read_csv("user.csv")
        else:
            users = pd.DataFrame(columns=["email", "password"])

        if email in users['email'].values:
            return False

        new_user = pd.DataFrame({'email': [email], 'password': [password]})
        new_user.to_csv("user.csv", mode='a', header=not os.path.exists("user.csv"), index=False)
        return True

    except Exception as e:
        st.error(f"⚠️ Error registering user: {e}")
        return False

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = "login"


df = pd.read_csv("styles_updated.csv")
df['image_path'] = df['id'].astype(str).apply(lambda x: f"images/{x}.jpg")


def show_sidebar():
    with st.sidebar:
        return option_menu(
            menu_title="ShopSense Menu",
            options=["Home", "Recommendation", "Dataset", "About", "Logout"],
            icons=["house", "search", "table", "info-circle", "box-arrow-left"],
            default_index=0,
            orientation="vertical"
        )


def login_page():
    st.title("🔐 Login to ShopSense")
    users_df = load_users()

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if check_login(email, password, users_df):
                st.session_state.logged_in = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid email or password")

    st.markdown("---")
    if st.button("Don't have an account? Register"):
        st.session_state.page = "register"
        st.rerun()


def register_page():
    st.title("📝 Register New Account")

    with st.form("register_form"):
        new_email = st.text_input("Email")
        new_pass = st.text_input("Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")

        if submit:
            if new_pass != confirm_pass:
                st.error("❌ Passwords do not match!")
            elif register_user(new_email, new_pass):
                st.success("✅ Registered successfully! Logging you in...")
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Email already registered.")

    st.markdown("---")
    if st.button("Already have an account? Login"):
        st.session_state.page = "login"
        st.rerun()


def logout():
    st.session_state.logged_in = False
    st.session_state.page = "login"
    st.rerun()


if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "register":
        register_page()
else:
    selected = show_sidebar()

    if selected == "Home":
        st.title("🛍️ ShopSense - AI Product Recommendation")
        st.write("Welcome to your personalized fashion assistant!")

    elif selected == "Recommendation":
        st.title("🔍 Search & Recommend Products")
        user_input = st.text_input("Search (e.g., 'men shirt', 'women blue jeans')")

        if user_input:
            results = recommend_products(user_input)
            if results.empty:
                st.warning("❌ No matching products found.")
            else:
                for _, row in results.iterrows():
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        if os.path.exists(row['image_path']):
                            st.image(row['image_path'], width=200)
                        else:
                            st.text("Image not found")

                    with col2:
                        st.markdown(f"### {row.get('productDisplayName', 'N/A')}")
                        st.write(f"🗂️ **Category:** {row.get('subCategory', 'N/A')}")
                        st.write(f"🎨 **Color:** {row.get('baseColour', 'N/A')}")
                        st.write(f"👕 **Type:** {row.get('articleType', 'N/A')}")
                        st.write(f"🧍 **Gender:** {row.get('gender', 'N/A')}")
                        st.write(f"💰 **Price:** ₹{row.get('Price (INR)', 'N/A')}")
                        st.write(f"⭐ **Rating:** {row.get('rating', 'N/A')}")
                        st.write(f"📦 **In Stock:** {row.get('inStock', 'N/A')}")
                    st.markdown("---")

    elif selected == "Dataset":
        st.title("📊 Product Dataset")
        st.dataframe(df.head(100))

    elif selected == "About":
        st.title("ℹ️ About ShopSense")
        st.markdown("""
        ShopSense is an AI-powered product recommendation system built with machine learning.  
        - Recommends clothing products based on search.
        - Filters based on color, rating, category, and type.
        - Built using Python, Streamlit, Pandas, and Scikit-learn.
        """)

    elif selected == "Logout":
        logout()
