import mysql.connector
from mysql.connector import errorcode

def create_database(cursor):
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS ResumeDatabase DEFAULT CHARACTER SET 'utf8mb4';")
    except mysql.connector.Error as err:
        print(f"Failed to create database: {err}")
        exit(1)

def create_tables(cursor):
    # Use the database
    cursor.execute("USE ResumeDatabase;")

    # Candidates table
    candidates_table = (
        """CREATE TABLE IF NOT EXISTS Candidates (
        candidate_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        phone_number VARCHAR(20),
        location VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )

    # Education table
    education_table = (
        """CREATE TABLE IF NOT EXISTS Education (
        education_id INT AUTO_INCREMENT PRIMARY KEY,
        candidate_id INT NOT NULL,
        degree VARCHAR(255),
        institution VARCHAR(255),
        graduation_year YEAR,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )"""
    )

    # WorkExperience table
    work_experience_table = (
        """CREATE TABLE IF NOT EXISTS WorkExperience (
        work_id INT AUTO_INCREMENT PRIMARY KEY,
        candidate_id INT NOT NULL,
        position VARCHAR(255),
        company VARCHAR(255),
        years_experience INT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )"""
    )

    # Skills table
    skills_table = (
        """CREATE TABLE IF NOT EXISTS Skills (
        skill_id INT AUTO_INCREMENT PRIMARY KEY,
        candidate_id INT NOT NULL,
        skill_name VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )"""
    )

    emdeddings_table = (
        """
        CREATE TABLE IF NOT EXISTS ResumeEmbeddings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        candidate_id INT NOT NULL,
        embedding TEXT NOT NULL,
        FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )
        """
    )

    # Execute table creation
    tables = [candidates_table, education_table, work_experience_table, skills_table,emdeddings_table]
    for table in tables:
        try:
            cursor.execute(table)
        except mysql.connector.Error as err:
            print(f"Failed to create table: {err}")
            exit(1)

def main():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Emug123$'
        )
        cursor = connection.cursor()

        # Create database and tables
        create_database(cursor)
        create_tables(cursor)

        print("Database and tables created successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Invalid username or password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist.")
        else:
            print(err)
    finally:
        # Close the connection
        if 'cnx' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    main()