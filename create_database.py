

def create_tables(connection):
    """
    Create tables in SQLite database with proper schema and relationships.
    Includes error handling for table creation failures.
    """
    # Define table schemas using SQLite syntax
    tables = [
        """CREATE TABLE IF NOT EXISTS Candidates (
            candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS Education (
            education_id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            degree TEXT,
            institution TEXT,
            graduation_year INTEGER,  -- SQLite doesn't have YEAR type
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS WorkExperience (
            work_id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            position TEXT,
            company TEXT,
            years_experience INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS Skills (
            skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            skill_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS ResumeEmbeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            embedding TEXT NOT NULL,
            FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )""",
        """CREATE TABLE CandidateFeedback (
            feedback_id INT PRIMARY KEY AUTO_INCREMENT,
            candidate_id INT,
            feedback TEXT NOT NULL,
            reviewer VARCHAR(255) NOT NULL,
            FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )"""
    ]

    cursor = connection.cursor()
    try:

        # Create tables sequentially
        for table in tables:
            try:
                cursor.execute(table)
            except sqlite3.Error as err:
                print(f"Failed to create table: {err}")
                connection.rollback()
                exit(1)
        connection.commit()
    except sqlite3.Error as err:
        print(f"Database error: {err}")
        connection.rollback()
        exit(1)
    finally:
        cursor.close()


def main():
    """
    Main function to handle database creation and connection.
    Implements comprehensive error handling for database operations.
    """
    connection = None
    try:
        # Connect to SQLite database (creates if doesn't exist)
        connection = sqlite3.connect('ResumeDatabase.db')
        print("SQLite database connection established")

        # Create tables with error handling
        create_tables(connection)
        print("Tables created successfully")

    except sqlite3.Error as err:
        print(f"Database connection error: {err}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)
    finally:
        # Ensure connection is properly closed
        if connection:
            try:
                connection.close()
                print("Database connection closed")
            except sqlite3.Error as err:
                print(f"Error closing connection: {err}")
                exit(1)


if __name__ == "__main__":
    main()