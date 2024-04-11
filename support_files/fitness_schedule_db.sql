CREATE DATABASE fitness_schedule_db;

USE fitness_schedule_db;

CREATE TABLE Members (
	member_id INT AUTO_INCREMENT PRIMARY KEY,
    member_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(15),
	membership_type VARCHAR(30)
);

CREATE TABLE Workout_Sessions (
	session_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    session_date DATETIME,
    workout_type VARCHAR(100),
    FOREIGN KEY (member_id) REFERENCES Members(member_id)
);

INSERT INTO Members(member_name, email, phone, membership_type)
VALUES ("Tony Stark", "t@stark.ind", "212-470-6626", "Gold Membership");

INSERT INTO Workout_Sessions(member_id, session_date, workout_type)
VALUES (1, "2012-04-10 09:00:00", "Cardio");

SELECT * 
FROM Members;

SELECT *
FROM Workout_Sessions;