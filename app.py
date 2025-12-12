import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Student Management App", layout="wide")
st.title("📚 Student Management System")

# ========================
# Database Configuration
# ========================

DATABASE_NAME = "data.db"

def init_database():
    """
    Initialize the SQLite database and create the students table if it doesn't exist.
    This function is called on app startup.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Create table with student information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            course TEXT NOT NULL,
            enrollment_date TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# ========================
# Database Functions (CRUD)
# ========================

def insert_student(name, email, phone, course):
    """
    CREATE operation: Insert a new student record into the database.
    
    Args:
        name (str): Student's full name
        email (str): Student's email address
        phone (str): Student's phone number
        course (str): Course name
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    enrollment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO students (name, email, phone, course, enrollment_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, email, phone, course, enrollment_date))
    
    conn.commit()
    conn.close()

def view_all_students():
    """
    READ operation: Retrieve all student records from the database.
    
    Returns:
        DataFrame: Pandas DataFrame containing all student records
    """
    conn = sqlite3.connect(DATABASE_NAME)
    query = "SELECT id, name, email, phone, course, enrollment_date FROM students"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_student_by_id(student_id):
    """
    Helper function: Retrieve a specific student record by ID.
    
    Args:
        student_id (int): Student ID to retrieve
        
    Returns:
        tuple: Student record data or None if not found
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

def update_student(student_id, name, email, phone, course):
    """
    UPDATE operation: Modify an existing student record.
    
    Args:
        student_id (int): ID of the student to update
        name (str): Updated student name
        email (str): Updated email address
        phone (str): Updated phone number
        course (str): Updated course name
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE students 
        SET name = ?, email = ?, phone = ?, course = ?
        WHERE id = ?
    ''', (name, email, phone, course, student_id))
    
    conn.commit()
    conn.close()

def delete_student(student_id):
    """
    DELETE operation: Remove a student record from the database.
    
    Args:
        student_id (int): ID of the student to delete
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()

# ========================
# Initialize Database
# ========================

init_database()

# ========================
# Streamlit UI
# ========================

# Sidebar navigation
st.sidebar.title("📋 Navigation")
operation = st.sidebar.radio(
    "Select an operation:",
    ["➕ Create", "📖 View", "✏️ Update", "🗑️ Delete"]
)

# ========================
# CREATE OPERATION
# ========================

if operation == "➕ Create":
    st.header("Add New Student")
    st.info("Fill in the form below to add a new student to the database.")
    
    with st.form("add_student_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email Address", placeholder="john@example.com")
        
        with col2:
            phone = st.text_input("Phone Number", placeholder="123-456-7890")
            course = st.selectbox(
                "Course",
                ["Python Programming", "Web Development", "Data Science", 
                 "Machine Learning", "Database Design", "Mobile App Development"]
            )
        
        submit_button = st.form_submit_button("✅ Add Student", use_container_width=True)
        
        if submit_button:
            # Validate input
            if name and email and phone and course:
                insert_student(name, email, phone, course)
                st.success("✅ Student added successfully!")
                st.balloons()
            else:
                st.error("❌ Please fill in all fields.")

# ========================
# READ OPERATION
# ========================

elif operation == "📖 View":
    st.header("All Students")
    st.info("View all student records in the database.")
    
    df = view_all_students()
    
    if not df.empty:
        # Display the dataframe with formatting
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "name": st.column_config.TextColumn("Name", width="medium"),
                "email": st.column_config.TextColumn("Email", width="medium"),
                "phone": st.column_config.TextColumn("Phone", width="small"),
                "course": st.column_config.TextColumn("Course", width="medium"),
                "enrollment_date": st.column_config.TextColumn("Enrollment Date", width="medium")
            }
        )
        
        # Summary statistics
        st.subheader("📊 Summary Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Students", len(df))
        with col2:
            st.metric("Unique Courses", df['course'].nunique())
        with col3:
            st.metric("Records in Database", len(df))
    else:
        st.warning("⚠️ No students found in the database. Add some students first!")

# ========================
# UPDATE OPERATION
# ========================

elif operation == "✏️ Update":
    st.header("Update Student Information")
    st.info("Select a student and modify their information.")
    
    df = view_all_students()
    
    if not df.empty:
        # Dropdown to select student
        student_names = df['name'].tolist()
        selected_name = st.selectbox("Select Student to Update", student_names)
        
        # Get the selected student's data
        selected_student = df[df['name'] == selected_name].iloc[0]
        student_id = selected_student['id']
        
        st.write("---")
        st.subheader(f"Editing: {selected_name}")
        
        with st.form("update_student_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input(
                    "Full Name",
                    value=selected_student['name']
                )
                new_email = st.text_input(
                    "Email Address",
                    value=selected_student['email']
                )
            
            with col2:
                new_phone = st.text_input(
                    "Phone Number",
                    value=selected_student['phone']
                )
                new_course = st.selectbox(
                    "Course",
                    ["Python Programming", "Web Development", "Data Science", 
                     "Machine Learning", "Database Design", "Mobile App Development"],
                    index=["Python Programming", "Web Development", "Data Science", 
                           "Machine Learning", "Database Design", "Mobile App Development"].index(selected_student['course'])
                )
            
            # Display current enrollment date
            st.caption(f"Enrolled: {selected_student['enrollment_date']}")
            
            submit_button = st.form_submit_button("💾 Save Changes", use_container_width=True)
            
            if submit_button:
                if new_name and new_email and new_phone and new_course:
                    update_student(student_id, new_name, new_email, new_phone, new_course)
                    st.success("✅ Student information updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please fill in all fields.")
    else:
        st.warning("⚠️ No students found in the database. Add some students first!")

# ========================
# DELETE OPERATION
# ========================

elif operation == "🗑️ Delete":
    st.header("Delete Student")
    st.warning("⚠️ Warning: Deleting a student is permanent and cannot be undone.")
    
    df = view_all_students()
    
    if not df.empty:
        # Dropdown to select student to delete
        student_names = df['name'].tolist()
        selected_name = st.selectbox("Select Student to Delete", student_names)
        
        # Get the selected student's data
        selected_student = df[df['name'] == selected_name].iloc[0]
        student_id = selected_student['id']
        
        # Display student information before deletion
        st.write("---")
        st.subheader("Student Details (To Be Deleted)")
        
        info_df = pd.DataFrame({
            "Field": ["Name", "Email", "Phone", "Course", "Enrolled"],
            "Value": [
                selected_student['name'],
                selected_student['email'],
                selected_student['phone'],
                selected_student['course'],
                selected_student['enrollment_date']
            ]
        })
        
        st.dataframe(info_df, hide_index=True, use_container_width=True)
        
        st.write("---")
        
        # Confirmation and delete button
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Delete Student", type="primary", use_container_width=True):
                delete_student(student_id)
                st.success("✅ Student deleted successfully!")
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.info("Deletion cancelled.")
    else:
        st.warning("⚠️ No students found in the database. Add some students first!")

# ========================
# Footer
# ========================

st.write("---")
st.caption("💡 Student Management System | Built with Streamlit & SQLite3")
