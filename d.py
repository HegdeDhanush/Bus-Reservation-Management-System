import streamlit as st
import mysql.connector
from mysql.connector import Error
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime, date

def get_database_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="9448522402",
            database="bus_mgmt"
        )
    except Error as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# Existing functions remain the same...
# Add new functions for complaints and tickets

def create_bus_route(route_name: str, source: str, destination: str, 
                    distance: str, duration: str, fare: str) -> bool:
    """Create a new bus route in the database."""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        # Convert fare to float for decimal handling
        fare_decimal = float(fare)
        
        cursor.callproc('CreateBusRoute', (
            route_name, source, destination, distance, duration, fare_decimal
        ))
        
        conn.commit()
        st.success("Bus route created successfully!")
        return True
        
    except Error as e:
        st.error(f"Error creating bus route: {e}")
        return False
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_users() -> List[Dict[str, Any]]:
    """Retrieve all users from the database."""
    conn = get_database_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT User_ID, Username, email, Role
            FROM users
            ORDER BY Username
        """)
        users = cursor.fetchall()
        return users
            
    except Error as e:
        st.error(f"Error retrieving users: {e}")
        return []
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_notification(user_id: int, message: str) -> bool:
    """Create a new notification for a specific user."""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.callproc('CreateNotification', (user_id, message))
        conn.commit()
        st.success("Notification sent successfully!")
        return True
        
    except Error as e:
        st.error(f"Error creating notification: {e}")
        return False
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
def get_notifications(user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Retrieve notifications from the database.
    If user_id is provided, returns notifications for that user only.
    """
    conn = get_database_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        if user_id:
            # Get notifications for specific user
            cursor.execute("""
                SELECT n.Notification_ID, n.Message, n.Created_At,
                       u.Username as Recipient
                FROM notifications n
                JOIN users u ON n.User_ID = u.User_ID
                WHERE n.User_ID = %s
                ORDER BY n.Created_At DESC
            """, (user_id,))
        else:
            # Admin view - get all notifications
            cursor.execute("""
                SELECT n.Notification_ID, n.Message, n.Created_At,
                       u.Username as Recipient
                FROM notifications n
                JOIN users u ON n.User_ID = u.User_ID
                ORDER BY n.Created_At DESC
            """)
        notifications = cursor.fetchall()
        return notifications
            
    except Error as e:
        st.error(f"Error retrieving notifications: {e}")
        return []
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get user details by username"""
    conn = get_database_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT User_ID, Username, email, Role
            FROM users
            WHERE Username = %s
        """, (username,))
        return cursor.fetchone()
            
    except Error as e:
        st.error(f"Error retrieving user: {e}")
        return None
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_notification(user_id: int, message: str) -> bool:
    """Create a new notification for a specific user."""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.callproc('CreateNotification', (user_id, message))
        conn.commit()
        st.success("Notification sent successfully!")
        return True
        
    except Error as e:
        st.error(f"Error creating notification: {e}")
        return False
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def display_notifications_table(notifications: List[Dict[str, Any]]) -> None:
    """Helper function to display notifications in a formatted table"""
    if notifications:
        st.write("### Notifications")
        for n in notifications:
            with st.expander(f"Notification from {n['Created_At'].strftime('%Y-%m-%d %H:%M')}"):
                st.write(f"**To:** {n['Recipient']}")
                st.write(n['Message'])
    else:
        st.info("No notifications found")

def get_user_notifications(user_id: int) -> List[Dict[str, Any]]:
    """Retrieve notifications for a specific user."""
    conn = get_database_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('GetUserNotifications', (user_id,))
        
        notifications = []
        for result in cursor.stored_results():
            notifications = result.fetchall()
        
        return notifications
            
    except Error as e:
        st.error(f"Error retrieving user notifications: {e}")
        return []
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

            
def display_bus_routes() -> List[Dict[str, Any]]:
    """Retrieve all bus routes from the database."""
    conn = get_database_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT Route_ID, RouteName, Source, Destination, 
                   Distance, Duration, Fare, Available_Seats
            FROM bus_routes
            ORDER BY Route_ID
        """)
        routes = cursor.fetchall()
        return routes
            
    except Error as e:
        st.error(f"Error retrieving bus routes: {e}")
        return []
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def check_admin_login(username: str, password: str) -> tuple[bool, Optional[dict]]:
    """Verify administrator login credentials and return user data if successful."""
    conn = get_database_connection()
    if not conn:
        return False, None
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Hash the password using SHA-256
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Check admin credentials
        cursor.execute("""
            SELECT Admin_ID, Username, Role
            FROM Administrators
            WHERE Username = %s AND Password = %s
        """, (username, hashed_password))
        
        admin_data = cursor.fetchone()
        
        if admin_data:
            return True, admin_data
        return False, None
        
    except Error as e:
        st.error(f"Error during admin login: {e}")
        return False, None
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()




def register_new_operator(username: str, password: str, first_name: str, last_name: str, email: str) -> bool:
    """Register a new bus operator in the system."""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Hash the password using SHA-256
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.callproc('RegisterOperator', (
            username, hashed_password, first_name, last_name, email
        ))
        
        result = None
        for result_cursor in cursor.stored_results():
            result = result_cursor.fetchone()
        
        conn.commit()
        
        if result and result['result'] == 'SUCCESS':
            st.success("Operator registered successfully!")
            return True
        elif result and result['result'] == 'DUPLICATE':
            st.error("Username or email already exists")
            return False
            
        return False
        
    except Error as e:
        st.error(f"Error registering operator: {e}")
        return False
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def check_operator_login(username: str, password: str) -> tuple[bool, Optional[dict]]:
    """Verify operator login credentials and return user data if successful."""
    conn = get_database_connection()
    if not conn:
        return False, None
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Hash the password using SHA-256
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.callproc('CheckOperatorLogin', (username, hashed_password))
        
        result = None
        for result_cursor in cursor.stored_results():
            result = result_cursor.fetchone()
        
        if result and result['result'] == 'SUCCESS':
            # Get operator details
            cursor.execute("""
                SELECT Operator_ID, Username, First_Name, Last_Name, Email, Status
                FROM Operators WHERE Username = %s
            """, (username,))
            operator_data = cursor.fetchone()
            return True, operator_data
            
        return False, None
        
    except Error as e:
        st.error(f"Error during login: {e}")
        return False, None
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_complaint(operator_id: int, subject: str, message: str) -> bool:
    """Create a new complaint in the database."""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.callproc('CreateComplaint', (operator_id, subject, message))
        conn.commit()
        st.success("Complaint submitted successfully")
        return True
        
    except Error as e:
        st.error(f"Error submitting complaint: {e}")
        return False
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_complaints() -> List[Dict[str, Any]]:
    """Retrieve all complaints from the database."""
    conn = get_database_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('GetComplaintList')
        
        complaints = []
        for result in cursor.stored_results():
            complaints = result.fetchall()
        
        return complaints
            
    except Error as e:
        st.error(f"Error retrieving complaints: {e}")
        return []
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def update_complaint_status(complaint_id: int, status: str) -> bool:
    """Update the status of a complaint."""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.callproc('UpdateComplaintStatus', (complaint_id, status))
        conn.commit()
        st.success(f"Complaint status updated to {status}")
        return True
        
    except Error as e:
        st.error(f"Error updating complaint status: {e}")
        return False
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def book_ticket(route_id: int, passenger_name: str, passenger_email: str, 
                passenger_phone: str, booking_date: date, num_seats: int) -> bool:
    """Book a new ticket."""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('BookTicket', (
            route_id, passenger_name, passenger_email,
            passenger_phone, booking_date, num_seats
        ))
        
        result = None
        for result_cursor in cursor.stored_results():
            result = result_cursor.fetchone()
        
        conn.commit()
        
        if result and result['result'] == 'SUCCESS':
            st.success("Ticket booked successfully!")
            return True
        elif result and result['result'] == 'INSUFFICIENT_SEATS':
            st.error("Not enough seats available")
            return False
            
        return False
        
    except Error as e:
        st.error(f"Error booking ticket: {e}")
        return False
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def cancel_ticket(ticket_id: int) -> bool:
    """Cancel a ticket."""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('CancelTicket', (ticket_id,))
        
        result = None
        for result_cursor in cursor.stored_results():
            result = result_cursor.fetchone()
        
        conn.commit()
        
        if result and result['result'] == 'SUCCESS':
            st.success("Ticket cancelled successfully!")
            return True
        elif result and result['result'] == 'ALREADY_CANCELLED':
            st.error("Ticket is already cancelled")
            return False
            
        return False
        
    except Error as e:
        st.error(f"Error cancelling ticket: {e}")
        return False
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_route_tickets(route_id: int) -> List[Dict[str, Any]]:
    """Get all tickets for a specific route."""
    conn = get_database_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('GetRouteTickets', (route_id,))
        
        tickets = []
        for result in cursor.stored_results():
            tickets = result.fetchall()
        
        return tickets
            
    except Error as e:
        st.error(f"Error retrieving tickets: {e}")
        return []
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
def display_bus_routes_table(routes):
    """Helper function to display bus routes in a formatted table"""
    if routes:
        st.write("### Bus Routes List")
        route_data = []
        for r in routes:
            route_data.append({
                "ID": r["Route_ID"],
                "Name": r["RouteName"],
                "Source": r["Source"],
                "Destination": r["Destination"],
                "Distance": r["Distance"],
                "Duration": r["Duration"],
                "Fare": f"₹{r['Fare']}",
                "Available Seats": r["Available_Seats"]
            })
        st.table(route_data)

def display_complaints_table(complaints):
    """Helper function to display complaints in a formatted table"""
    if complaints:
        st.write("### Complaints List")
        for c in complaints:
            with st.expander(f"Complaint #{c['Complaint_ID']} - {c['Subject']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Operator:** {c['Operator_Name']}")
                with col2:
                    st.write(f"**Status:** {c['Status']}")
                with col3:
                    st.write(f"**Date:** {c['Created_At'].strftime('%Y-%m-%d %H:%M')}")
                
                st.write("**Message:**")
                st.write(c['Message'])
                
                # Add status update option for admin
                if st.session_state.get('user_type') == 'admin':
                    new_status = st.selectbox(
                        "Update Status",
                        ['Pending', 'In Progress', 'Resolved'],
                        key=f"status_{c['Complaint_ID']}",
                        index=['Pending', 'In Progress', 'Resolved'].index(c['Status'])
                    )
                    if new_status != c['Status']:
                        if st.button("Update Status", key=f"update_{c['Complaint_ID']}"):
                            update_complaint_status(c['Complaint_ID'], new_status)
                            st.rerun()

def display_route_tickets(route_id):
    """Helper function to display tickets for a route"""
    tickets = get_route_tickets(route_id)
    if tickets:
        st.write("### Ticket List")
        for t in tickets:
            with st.expander(f"Ticket #{t['Ticket_ID']} - {t['Passenger_Name']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Booking Date:** {t['Booking_Date']}")
                with col2:
                    st.write(f"**Seats:** {t['Number_Of_Seats']}")
                with col3:
                    st.write(f"**Status:** {t['Status']}")
                
                st.write(f"**Email:** {t['Passenger_Email']}")
                st.write(f"**Phone:** {t['Passenger_Phone']}")
                st.write(f"**Total Fare:** ₹{t['Total_Fare']}")
                
                if t['Status'] == 'Booked':
                    if st.button("Cancel Ticket", key=f"cancel_{t['Ticket_ID']}"):
                        if cancel_ticket(t['Ticket_ID']):
                            st.rerun()

def admin_portal():
    st.title("Bus Ticket Administration Portal")
    st.write(f"Welcome, {st.session_state['user_data']['Username']}")
    
    menu = st.sidebar.selectbox(
        "Menu",
        ["Create Bus Route", "Display Bus Routes",
         "Create Notification", "Display Notifications",
         "View Complaints"]
    )
    
    if st.sidebar.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

    if menu == "Create Bus Route":
        st.header("Create New Bus Route")
        with st.form("route_form"):
            route_name = st.text_input("Route Name")
            source = st.text_input("Source Location")
            destination = st.text_input("Destination")
            distance = st.text_input("Distance (km)")
            duration = st.text_input("Duration (hours)")
            fare = st.number_input("Fare (₹)", min_value=0.0, step=0.5)
            
            if st.form_submit_button("Create Route"):
                if all([route_name, source, destination, distance, duration, str(fare)]):
                    create_bus_route(route_name, source, destination, distance, duration, str(fare))
                else:
                    st.error("All fields are required")
    
    elif menu == "Display Bus Routes":
        st.header("All Bus Routes")
        routes = display_bus_routes()
        display_bus_routes_table(routes)
        
        # Display tickets for each route
        if routes:
            st.write("### Route Tickets")
            selected_route = st.selectbox(
                "Select Route to View Tickets",
                options=[r['RouteName'] for r in routes],
                key="admin_route_select"
            )
            selected_route_id = next(r['Route_ID'] for r in routes if r['RouteName'] == selected_route)
            display_route_tickets(selected_route_id)

    elif menu == "Create Notification":
        st.header("Create New Notification")
        users = get_users()
        
        with st.form("notification_form"):
            user_options = {f"{user['Username']} (ID: {user['User_ID']})": user['User_ID'] 
                          for user in users}
            
            if user_options:
                selected_user = st.selectbox("Select User", options=list(user_options.keys()))
                message = st.text_area("Notification Message")
                
                if st.form_submit_button("Create Notification"):
                    if message:
                        user_id = user_options[selected_user]
                        create_notification(user_id, message)
                    else:
                        st.error("Please enter a message")
            else:
                st.error("No users found in the system")
                st.form_submit_button("Create Notification", disabled=True)

    elif menu == "Display Notifications":
        st.header("All Notifications")
        notifications = get_notifications()
        display_notifications_table(notifications)
        
    elif menu == "View Complaints":
        st.header("Operator Complaints")
        complaints = get_complaints()
        display_complaints_table(complaints)
        

def operator_portal():
    st.title("Bus Operator Portal")
    st.write(f"Welcome, {st.session_state['user_data']['Username']}")
    
    menu = st.sidebar.selectbox(
        "Menu",
        ["View Routes", "View Notifications", "Submit Complaint", "Book Tickets"]
    )
    
    if st.sidebar.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    
    if menu == "View Routes":
        st.header("All Bus Routes")
        routes = display_bus_routes()
        display_bus_routes_table(routes)
        
    elif menu == "View Notifications":
        st.header("Notifications")
        notifications = get_notifications()
        display_notifications_table(notifications)
        
    elif menu == "Submit Complaint":
        st.header("Submit New Complaint")
        with st.form("complaint_form"):
            subject = st.text_input("Subject")
            message = st.text_area("Complaint Details")
            
            if st.form_submit_button("Submit Complaint"):
                if subject and message:
                    operator_id = st.session_state['user_data']['Operator_ID']
                    create_complaint(operator_id, subject, message)
                else:
                    st.error("Please fill in all fields")
                    
    elif menu == "Book Tickets":
        st.header("Book Bus Tickets")
        routes = display_bus_routes()
        
        if routes:
            with st.form("booking_form"):
                # Route selection
                route_options = {f"{r['RouteName']} ({r['Source']} to {r['Destination']})": r['Route_ID'] 
                               for r in routes if r['Available_Seats'] > 0}
                
                if route_options:
                    selected_route = st.selectbox(
                        "Select Route",
                        options=list(route_options.keys())
                    )
                    
                    # Get selected route details
                    selected_route_id = route_options[selected_route]
                    route_details = next(r for r in routes if r['Route_ID'] == selected_route_id)
                    
                    st.write(f"Available Seats: {route_details['Available_Seats']}")
                    st.write(f"Fare per seat: ₹{route_details['Fare']}")
                    
                    # Passenger details
                    col1, col2 = st.columns(2)
                    with col1:
                        passenger_name = st.text_input("Passenger Name")
                        passenger_email = st.text_input("Email")
                    with col2:
                        passenger_phone = st.text_input("Phone")
                        num_seats = st.number_input("Number of Seats", 
                                                  min_value=1, 
                                                  max_value=route_details['Available_Seats'])
                    
                    booking_date = st.date_input("Travel Date")
                    total_fare = float(route_details['Fare']) * num_seats
                    st.write(f"Total Fare: ₹{total_fare}")
                    
                    if st.form_submit_button("Book Ticket"):
                        if all([passenger_name, passenger_email, passenger_phone]):
                            book_ticket(
                                selected_route_id,
                                passenger_name,
                                passenger_email,
                                passenger_phone,
                                booking_date,
                                num_seats
                            )
                        else:
                            st.error("Please fill in all passenger details")
                else:
                    st.error("No routes available for booking")
                    st.form_submit_button("Book Ticket", disabled=True)
        
        # Show booked tickets
        st.header("Manage Bookings")
        if routes:
            selected_route = st.selectbox(
                "Select Route to View Bookings",
                options=[r['RouteName'] for r in routes],
                key="operator_route_select"
            )
            selected_route_id = next(r['Route_ID'] for r in routes if r['RouteName'] == selected_route)
            display_route_tickets(selected_route_id)
    elif menu == "View Notifications":
        st.header("My Notifications")
        # Get operator's user record
        operator_username = st.session_state['user_data']['Username']
        user_data = get_user_by_username(operator_username)
        
        if user_data:
            # Show only notifications for this operator
            notifications = get_notifications(user_data['User_ID'])
            display_notifications_table(notifications)
        else:
            st.error("Unable to retrieve notifications. Please contact administrator.")
    

def login_page():
    st.title("Bus Ticket Booking System")
    
    login_type = st.radio("Select Login Type", ["Bus Operator", "Administrator"])
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if login_type == "Administrator":
                success, user_data = check_admin_login(username, password)
                if success:
                    st.session_state['logged_in'] = True
                    st.session_state['user_type'] = 'admin'
                    st.session_state['user_data'] = user_data
                    st.success(f"Welcome, Administrator {username}!")
                    st.rerun()
                else:
                    st.error("Invalid administrator credentials")
            else:
                success, user_data = check_operator_login(username, password)
                if success:
                    st.session_state['logged_in'] = True
                    st.session_state['user_type'] = 'operator'
                    st.session_state['user_data'] = user_data
                    st.success(f"Welcome, Bus Operator {username}!")
                    st.rerun()
                else:
                    st.error("Invalid operator credentials")

def register_page():
    st.title("Bus Operator Registration")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
            username = st.text_input("Username")
            email = st.text_input("Email")
         
        with col2:
            last_name = st.text_input("Last Name")
            password = st.text_input("Password", type="password")
            password_confirm = st.text_input("Confirm Password", type="password")
        
        if st.form_submit_button("Register"):
            if not all([username, password, first_name, last_name, email]):
                st.error("All fields are required")
            elif password != password_confirm:
                st.error("Passwords do not match")
            else:
                register_new_operator(username, password, first_name, last_name, email)

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if st.sidebar.button("Verify Admin Setup"):
        verify_admin_credentials()
    
    if st.session_state['logged_in']:
        if st.session_state['user_type'] == 'admin':
            admin_portal()
        else:
            operator_portal()
    else:
        page = st.sidebar.selectbox("Menu", ["Login", "Register"])
        if page == "Login":
            login_page()
        else:
            register_page()

if __name__ == "__main__":
    main()