import json

from mysql.connector import connect, errorcode, Error as MySQLError

from classes import EducationalProgram, Abitur
from config import HOST, PORT, USERNAME, PASSWORD, EP_ID_JSON


def save_ep_id_to_json() -> None:
    """"""
    get_query = """SELECT * FROM  EduProgs"""
    try:
        with connect(host=HOST, port=PORT, user=USERNAME, password=PASSWORD, database="belldh") as connection:
            with connection.cursor() as cursor:
                cursor.execute(get_query)
                educational_programs = cursor.fetchall()
                # print(educational_programs)
        ret = {}
        for prog in educational_programs:
            id_, un, code, name, *other = prog
            name = name.strip()
            if un not in ret.keys():
                ret[un] = {}
            if code not in ret[un].keys():
                ret[un][code] = {}
            ret[un][code][name] = id_
            # print(un, code, name)
        with open(EP_ID_JSON, "w", encoding="utf-8") as file:
            json.dump(ret, file, indent=4)

    except MySQLError as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(e)


def save_educational_programs(data: list[EducationalProgram]) -> None:
    """"""
    insert_query = """
        INSERT EduProgs 
        (uni_name, code, name, cnt_budget, cnt_special_quota, cnt_separate_quota, cnt_target_quota, cnt_contract, price)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s )
    """
    data_tuples =[ep.to_database_format() for ep in data]
    try:
        with connect(host=HOST, port=PORT, user=USERNAME, password=PASSWORD, database="belldh") as connection:
            with connection.cursor() as cursor:
                cursor.executemany(insert_query, data_tuples)
                connection.commit()

    except MySQLError as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(e)


def save_abiturs(data: list[Abitur]) -> None:
    """"""
    insert_query = """
        INSERT Abiturs 
        (inipa, original, place, score, payment, benefits, priority, edu_prog_id)
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s )
    """
    data_tuples = [ab.to_database_format() for ab in data]
    try:
        with connect(host=HOST, port=PORT, user=USERNAME, password=PASSWORD, database="belldh") as connection:
            with connection.cursor() as cursor:
                cursor.executemany(insert_query, data_tuples)
                connection.commit()

    except MySQLError as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(e)


if __name__ == '__main__':
    save_ep_id_to_json()
