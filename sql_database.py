import mysql.connector

mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Emug123$",
        database="ResumeDatabase"
    )

mycursor = mydb.cursor()

mycursor.execute("Show tables;")

myresult = mycursor.fetchall()

for x in myresult:
    print(x)

mycursor.execute( "SELECT * FROM Candidates")

myresult = mycursor.fetchall()

for x in myresult:
    print(x)
