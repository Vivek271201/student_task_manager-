import mysql.connector


# def get_db_connection():
#     """
#     Creates and returns a MySQL database connection.
#     """

#     connection = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="0905",     # Change according to your MySQL password
#         database="student_task_manager1"
#     )

#     return connection


def get_db_connection():
    connection = mysql.connector.connect(
        host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
        user="2AN3d7XAyUTwNz7.root",
        password="hHXMPwN7c6M5aFRs",     
        database="student_task_manager1",
        port=4000
    ) 

    return connection

