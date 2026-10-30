from database.DB_connect import DBConnect


class DAO():
    @staticmethod
    def getAllAlbums():
        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                select * from album
                """

        cursor.execute(query)

        for row in cursor:
            results.append(**row)

        cursor.close()
        conn.close()
        return results