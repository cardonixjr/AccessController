import mysql.connector
db = mysql.connector.connect(host="localhost",
                             user="root",
                             passwd="root")

cursor = db.cursor()
cursor.execute("DROP DATABASE IF EXISTS accessController0")
cursor.execute("CREATE DATABASE accessController0")
cursor.execute("USE accessController0")
cursor.execute("CREATE TABLE Trackers( \
               direction VARCHAR(20),\
               total int,\
               weekday smallint,\
               datetime DATETIME,\
               ID int PRIMARY KEY AUTO_INCREMENT)")
db.commit()

cursor.execute("CREATE DATABASE login")
cursor.execute("CREATE TABLE accounts(  \
               username VARCHAR(50) NOT NULL,  \
               password VARCHAR(255) NOT NULL,  \
               email VARCHAR(100) NOT NULL,  \
               id INT(11) NOT NULL AUTO_INCREMENT")
