from mysql.connector import connect, errorcode, Error as MySQLError
from config import HOST, USERNAME, PASSWORD


try:
    with connect(host=HOST, port=3306, user=USERNAME, password=PASSWORD, database="belldh") as connection:
        print(connection)

        command = "SELECT * FROM Unis"
        command2 = "INSERT Unis VALUES (31312, 'LOSHARA');"

        with connection.cursor() as cursor:
            cursor.execute(command2)
            connection.commit()

            # cursor.execute(command)
            # result = cursor.fetchall()
            # result = sorted(result, key=lambda x: x[0])
            # print(result)

except MySQLError as e:
    if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif e.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(e)

