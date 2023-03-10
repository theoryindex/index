import mysql.connector

def execute_query(query, params):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Q88prKdr!",
            database="index_db"
        )
        cursor = conn.cursor(dictionary=True)
        print(f'Query: {query}')
        print(f'Params: {params}')
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

    return results
