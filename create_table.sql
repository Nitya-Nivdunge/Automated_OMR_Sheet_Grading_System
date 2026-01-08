DROP DATABASE MCQ_Test_data;

CREATE DATABASE IF NOT EXISTS MCQ_Test_data;

USE MCQ_Test_data;

DROP TABLE student_scores;

CREATE TABLE IF NOT EXISTS student_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Rollno VARCHAR(50) NOT NULL,
    Subject VARCHAR(100) NOT NULL,
    Date DATE NOT NULL,
    Score INT NOT NULL,
    Grade CHAR(1) NOT NULL,
    Selected_Answers TEXT NOT NULL,
    Right_Ans INT NOT NULL,
    Wrong_Ans INT NOT NULL,
    Not_Answered INT NOT NULL
);