import mysql.connector

mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Emug123$",
        database="ResumeDatabase"
    )

mycursor = mydb.cursor()
mycursor.execute("""
        CREATE TABLE IF NOT EXISTS ResumeEmbeddings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            candidate_id INT NOT NULL,
            embedding TEXT NOT NULL,
            FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id) ON DELETE CASCADE
        )
        """)
mycursor.execute("Show tables;")
myresult = mycursor.fetchall()

for x in myresult:
    print(x)
