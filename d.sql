-- Drop and recreate database
DROP DATABASE IF EXISTS bus_mgmt;
CREATE DATABASE bus_mgmt;
USE bus_mgmt;

-- Create tables
-- Users table
CREATE TABLE users (
    User_ID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    Role ENUM('user', 'operator', 'conductor') NOT NULL,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bus Routes table
CREATE TABLE bus_routes (
    Route_ID INT PRIMARY KEY AUTO_INCREMENT,
    RouteName VARCHAR(100) NOT NULL,
    Source VARCHAR(100) NOT NULL,
    Destination VARCHAR(100) NOT NULL,
    Distance VARCHAR(50) NOT NULL,
    Duration VARCHAR(50) NOT NULL,
    Fare DECIMAL(10,2) NOT NULL,
    Available_Seats INT DEFAULT 30
);

-- Administrators table
CREATE TABLE Administrators (
    Admin_ID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Password VARCHAR(256) NOT NULL,
    Role VARCHAR(20) NOT NULL
);

-- Operators table
CREATE TABLE Operators (
    Operator_ID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Password VARCHAR(100) NOT NULL,
    First_Name VARCHAR(50) NOT NULL,
    Last_Name VARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Status ENUM('Active', 'Inactive') NOT NULL
);

-- Notifications table (updated with is_read flag)
CREATE TABLE notifications (
    Notification_ID INT PRIMARY KEY AUTO_INCREMENT,
    User_ID INT NOT NULL,
    Message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID) REFERENCES users(User_ID)
);

-- Complaints table
CREATE TABLE complaints (
    Complaint_ID INT PRIMARY KEY AUTO_INCREMENT,
    Operator_ID INT NOT NULL,
    Subject VARCHAR(200) NOT NULL,
    Message TEXT NOT NULL,
    Status ENUM('Pending', 'In Progress', 'Resolved') DEFAULT 'Pending',
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Operator_ID) REFERENCES Operators(Operator_ID)
);

-- Tickets table
CREATE TABLE tickets (
    Ticket_ID INT PRIMARY KEY AUTO_INCREMENT,
    Route_ID INT NOT NULL,
    Passenger_Name VARCHAR(100) NOT NULL,
    Passenger_Email VARCHAR(100) NOT NULL,
    Passenger_Phone VARCHAR(20) NOT NULL,
    Booking_Date DATE NOT NULL,
    Number_Of_Seats INT NOT NULL,
    Total_Fare DECIMAL(10,2) NOT NULL,
    Status ENUM('Booked', 'Cancelled') DEFAULT 'Booked',
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Route_ID) REFERENCES bus_routes(Route_ID)
);


-- Stored Procedures

-- Procedure to create a new complaint
DELIMITER //
CREATE PROCEDURE CreateComplaint(
    IN p_Operator_ID INT,
    IN p_Subject VARCHAR(200),
    IN p_Message TEXT
)
BEGIN
    INSERT INTO complaints (Operator_ID, Subject, Message)
    VALUES (p_Operator_ID, p_Subject, p_Message);
END //
DELIMITER ;

-- Procedure to get all complaints
DELIMITER //
CREATE PROCEDURE GetComplaintList()
BEGIN
    SELECT c.*, o.Username as Operator_Name 
    FROM complaints c
    JOIN Operators o ON c.Operator_ID = o.Operator_ID;
END //
DELIMITER ;

-- Procedure to update complaint status
DELIMITER //
CREATE PROCEDURE UpdateComplaintStatus(
    IN p_Complaint_ID INT,
    IN p_Status VARCHAR(20)
)
BEGIN
    UPDATE complaints 
    SET Status = p_Status 
    WHERE Complaint_ID = p_Complaint_ID;
END //
DELIMITER ;

-- Procedure to book a ticket
DELIMITER //
CREATE PROCEDURE BookTicket(
    IN p_Route_ID INT,
    IN p_Passenger_Name VARCHAR(100),
    IN p_Passenger_Email VARCHAR(100),
    IN p_Passenger_Phone VARCHAR(20),
    IN p_Booking_Date DATE,
    IN p_Number_Of_Seats INT
)
BEGIN
    DECLARE v_available_seats INT;
    DECLARE v_fare DECIMAL(10,2);
    DECLARE v_total_fare DECIMAL(10,2);
    
    -- Get available seats and fare
    SELECT Available_Seats, Fare INTO v_available_seats, v_fare
    FROM bus_routes WHERE Route_ID = p_Route_ID;
    
    IF v_available_seats >= p_Number_Of_Seats THEN
        -- Calculate total fare
        SET v_total_fare = v_fare * p_Number_Of_Seats;
        
        -- Create ticket
        INSERT INTO tickets (
            Route_ID, Passenger_Name, Passenger_Email, Passenger_Phone,
            Booking_Date, Number_Of_Seats, Total_Fare
        ) VALUES (
            p_Route_ID, p_Passenger_Name, p_Passenger_Email, p_Passenger_Phone,
            p_Booking_Date, p_Number_Of_Seats, v_total_fare
        );
        
        -- Update available seats
        UPDATE bus_routes 
        SET Available_Seats = Available_Seats - p_Number_Of_Seats
        WHERE Route_ID = p_Route_ID;
        
        SELECT 'SUCCESS' as result;
    ELSE
        SELECT 'INSUFFICIENT_SEATS' as result;
    END IF;
END //
DELIMITER ;

-- Procedure to cancel ticket
DELIMITER //
CREATE PROCEDURE CancelTicket(
    IN p_Ticket_ID INT
)
BEGIN
    DECLARE v_route_id INT;
    DECLARE v_seats INT;
    DECLARE v_current_status VARCHAR(20);
    
    -- Get ticket details
    SELECT Route_ID, Number_Of_Seats, Status 
    INTO v_route_id, v_seats, v_current_status
    FROM tickets WHERE Ticket_ID = p_Ticket_ID;
    
    IF v_current_status = 'Booked' THEN
        -- Update ticket status
        UPDATE tickets 
        SET Status = 'Cancelled' 
        WHERE Ticket_ID = p_Ticket_ID;
        
        -- Return seats to available pool
        UPDATE bus_routes 
        SET Available_Seats = Available_Seats + v_seats
        WHERE Route_ID = v_route_id;
        
        SELECT 'SUCCESS' as result;
    ELSE
        SELECT 'ALREADY_CANCELLED' as result;
    END IF;
END //
DELIMITER ;

-- Procedure to get tickets for a route
DELIMITER //
CREATE PROCEDURE GetRouteTickets(
    IN p_Route_ID INT
)
BEGIN
    SELECT * FROM tickets 
    WHERE Route_ID = p_Route_ID
    ORDER BY Created_At DESC;
END //
DELIMITER ;

-- Additional procedures and initial data

-- Updated CreateNotification procedure
DELIMITER //
CREATE PROCEDURE CreateNotification(
    IN p_User_ID INT,
    IN p_Message TEXT
)
BEGIN
    INSERT INTO notifications (User_ID, Message, is_read)
    VALUES (p_User_ID, p_Message, FALSE);
END //
DELIMITER ;

-- New procedure to mark notifications as read
DELIMITER //
CREATE PROCEDURE MarkNotificationAsRead(
    IN p_Notification_ID INT
)
BEGIN
    UPDATE notifications 
    SET is_read = TRUE 
    WHERE Notification_ID = p_Notification_ID;
END //
DELIMITER ;

-- Procedure to get user notifications
DELIMITER //
CREATE PROCEDURE GetUserNotifications(
    IN p_User_ID INT
)
BEGIN
    SELECT n.*, u.Username as Recipient
    FROM notifications n
    JOIN users u ON n.User_ID = u.User_ID
    WHERE n.User_ID = p_User_ID
    ORDER BY n.Created_At DESC;
END //
DELIMITER ;

-- Procedure to register new operator
DELIMITER //
CREATE PROCEDURE RegisterOperator(
    IN p_Username VARCHAR(50),
    IN p_Password VARCHAR(256),
    IN p_First_Name VARCHAR(50),
    IN p_Last_Name VARCHAR(50),
    IN p_Email VARCHAR(100)
)
BEGIN
    DECLARE user_exists INT;
    
    SELECT COUNT(*) INTO user_exists
    FROM Operators 
    WHERE Username = p_Username OR Email = p_Email;
    
    IF user_exists = 0 THEN
        INSERT INTO Operators (
            Username, Password, First_Name, Last_Name, Email, Status
        ) VALUES (
            p_Username, p_Password, p_First_Name, p_Last_Name, p_Email, 'Active'
        );
        SELECT 'SUCCESS' as result;
    ELSE
        SELECT 'DUPLICATE' as result;
    END IF;
END //
DELIMITER ;

-- Procedure to check operator login
DELIMITER //
CREATE PROCEDURE CheckOperatorLogin(
    IN p_Username VARCHAR(50),
    IN p_Password VARCHAR(256)
)
BEGIN
    DECLARE user_exists INT;
    
    SELECT COUNT(*) INTO user_exists
    FROM Operators 
    WHERE Username = p_Username 
    AND Password = p_Password
    AND Status = 'Active';
    
    IF user_exists = 1 THEN
        SELECT 'SUCCESS' as result;
    ELSE
        SELECT 'FAILURE' as result;
    END IF;
END //
DELIMITER ;

-- Create indices
CREATE INDEX idx_operator_username ON Operators(Username);
CREATE INDEX idx_operator_email ON Operators(Email);
CREATE INDEX idx_route_name ON bus_routes(RouteName);
CREATE INDEX idx_source_dest ON bus_routes(Source, Destination);
CREATE INDEX idx_notification_user ON notifications(User_ID, is_read);
CREATE INDEX idx_notification_date ON notifications(Created_At);

-- Insert initial data
INSERT INTO Administrators (Username, Password, Role) 
VALUES ('admin', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'administrator');

INSERT INTO users (Username, email, password, Role)
VALUES 
    ('testuser1', 'test1@example.com', 'testpass123', 'user'),
    ('operator1', 'operator1@example.com', 'testpass123', 'operator'),
    ('conductor1', 'conductor1@example.com', 'testpass123', 'conductor');

INSERT INTO Operators (Username, Password, First_Name, Last_Name, Email, Status)
VALUES (
    'testoperator',
    'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',
    'Test',
    'Operator',
    'testoperator@example.com',
    'Active'
);

INSERT INTO bus_routes (RouteName, Source, Destination, Distance, Duration, Fare, Available_Seats)
VALUES 
    ('Express-1', 'Bangalore', 'Mysore', '150 km', '3.5 hours', 450.00, 30),
    ('Express-2', 'Bangalore', 'Hassan', '180 km', '4 hours', 500.00, 30),
    ('Super-1', 'Mysore', 'Mangalore', '250 km', '6 hours', 750.00, 30);

INSERT INTO notifications (User_ID, Message)
SELECT User_ID, 'Welcome to the Bus Management System!' 
FROM users 
WHERE Username IN ('testuser1', 'operator1', 'conductor1');



-- Add this to your d.sql file after the other procedures

DELIMITER //
CREATE PROCEDURE CreateBusRoute(
    IN p_RouteName VARCHAR(100),
    IN p_Source VARCHAR(100),
    IN p_Destination VARCHAR(100),
    IN p_Distance VARCHAR(50),
    IN p_Duration VARCHAR(50),
    IN p_Fare DECIMAL(10,2)
)
BEGIN
    INSERT INTO bus_routes (
        RouteName,
        Source,
        Destination,
        Distance,
        Duration,
        Fare,
        Available_Seats
    ) VALUES (
        p_RouteName,
        p_Source,
        p_Destination,
        p_Distance,
        p_Duration,
        p_Fare,
        30  -- Default number of available seats
    );
END //
DELIMITER ;