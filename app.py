import streamlit as st
import pandas as pd
import json
import os

DATA_FILE = 'student_data.json'

# Function to load data from file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            return data.get('students', []), data.get('users', {'Shivansh': {'password': '451801', 'type': 'admin'}})
    return [], {'Shivansh': {'password': '451801', 'type': 'admin'}}

# Function to save data to file
def save_data(students, users):
    data = {'students': students, 'users': users}
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Initialize session state from file
students, users = load_data()
if 'students' not in st.session_state:
    st.session_state['students'] = students
if 'users' not in st.session_state:
    st.session_state['users'] = users
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_type' not in st.session_state:
    st.session_state['user_type'] = None

# Function to get student index
def get_student_index(rollno):
    for i, student in enumerate(st.session_state['students']):
        if student['Roll Number'] == rollno:
            return i
    return None

# Login/Register Page
def login_register():
    st.title("🔐 Student Information Portal - Login")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if username in st.session_state['users'] and st.session_state['users'][username]['password'] == password:
                st.session_state['logged_in'] = True
                st.session_state['user_type'] = st.session_state['users'][username]['type']
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    
    with tab2:
        st.subheader("Register as Viewer")
        new_username = st.text_input("New Username", key="reg_username")
        new_password = st.text_input("New Password", type="password", key="reg_password")
        # Automatically set as viewer; no choice for admin
        if st.button("Register"):
            if new_username in st.session_state['users']:
                st.error("Username already exists.")
            elif new_username and new_password:
                st.session_state['users'][new_username] = {'password': new_password, 'type': 'viewer'}
                save_data(st.session_state['students'], st.session_state['users'])  # Save after registration
                st.success("Registered successfully as viewer! Please login.")
            else:
                st.error("Please fill all fields.")

# Main App
if not st.session_state['logged_in']:
    login_register()
else:
    # Logout button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("📚 Student Information Portal")
    with col2:
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['user_type'] = None
            st.rerun()
    
    # Menu based on user type
    if st.session_state['user_type'] == 'admin':
        menu_options = ["View Students", "Add Student", "Update Student", "Delete Student"]
    else:
        menu_options = ["View Students"]
    
    menu = st.sidebar.selectbox("Menu", menu_options)
    
    if menu == "Add Student":
        st.header("➕ Add New Student")
        with st.form("add_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name")
                rollno = st.text_input("Roll Number")
            with col2:
                course = st.text_input("Course")
                marks = st.number_input("Marks", min_value=0, max_value=100, step=1)
            submitted = st.form_submit_button("Add Student")
            if submitted:
                if name and rollno and course:
                    st.session_state['students'].append({
                        "Name": name,
                        "Roll Number": rollno,
                        "Course": course,
                        "Marks": marks
                    })
                    save_data(st.session_state['students'], st.session_state['users'])  # Save after adding
                    st.success("✅ Student added successfully!")
                else:
                    st.error("Please fill all fields.")
    
    elif menu == "View Students":
        st.header("👀 All Students")
        if st.session_state['students']:
            df = pd.DataFrame(st.session_state['students'])
            st.dataframe(df, use_container_width=True)
            # Add some stats
            st.subheader("📊 Quick Stats")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Students", len(df))
            with col2:
                st.metric("Average Marks", round(df['Marks'].mean(), 2) if not df.empty else 0)
            with col3:
                st.metric("Highest Marks", df['Marks'].max() if not df.empty else 0)
        else:
            st.info("No students to display. Add some students first!")
    
    elif menu == "Update Student":
        st.header("✏️ Update Student Record")
        rollno = st.text_input("Enter Roll Number to Update")
        idx = get_student_index(rollno)
        if idx is not None:
            st.write("**Current Details:**")
            st.json(st.session_state['students'][idx])
            with st.form("update_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("New Name", value=st.session_state['students'][idx]['Name'])
                    new_course = st.text_input("New Course", value=st.session_state['students'][idx]['Course'])
                with col2:
                    new_marks = st.number_input("New Marks", min_value=0, max_value=100, value=int(st.session_state['students'][idx]['Marks']), step=1)
                if st.form_submit_button("Update Student"):
                    st.session_state['students'][idx]['Name'] = new_name
                    st.session_state['students'][idx]['Course'] = new_course
                    st.session_state['students'][idx]['Marks'] = new_marks
                    save_data(st.session_state['students'], st.session_state['users'])  # Save after updating
                    st.success("✅ Student record updated successfully!")
        elif rollno:
            st.error("❌ Roll Number not found.")
    
    elif menu == "Delete Student":
        st.header("🗑️ Delete Student Record")
        rollno = st.text_input("Enter Roll Number to Delete")
        idx = get_student_index(rollno)
        if idx is not None:
            st.warning(f"Are you sure you want to delete {st.session_state['students'][idx]['Name']}?")
            if st.button("Yes, Delete"):
                del st.session_state['students'][idx]
                save_data(st.session_state['students'], st.session_state['users'])  # Save after deleting
                st.success("✅ Student record deleted successfully!")
        elif rollno:
            st.error("❌ Roll Number not found.")

