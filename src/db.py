import sqlite3
from pathlib import Path


class sql():
    def __init__(self, path: str):
        PROJECT_ROOT = Path(__file__).resolve().parent.parent
        DB_PATH = PROJECT_ROOT / path

        self.con = sqlite3.connect(DB_PATH)

        if not self.con:
            print("Unable to connect to the database")
            self.connected = False

            raise

        self.cur = self.con.cursor()
        self.connected = True


    def close(self):
        self.con.close()


    def execute(self, query: str):
        if not self.connected:
            print("No DB connected")

            raise

        sanitized_query = query.strip().rstrip(";")
        first_token = sanitized_query.split()[0].upper() if sanitized_query else ""

        if first_token not in ("SELECT", "WITH"):
            return False, "Only read-only queries (SELECT, WITH) are authorized."

        res = self.cur.execute(sanitized_query)

        return res

    def get_scheme(self):
        if not self.connected:
            print("No DB connected")

            raise

        scheme = self.execute("""SELECT sql 
            FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name;""")

        return scheme

    def get_scheme_string(self):
        res = self.get_scheme()

        return "\n\n".join(row[0] for row in res.fetchall() if row[0])
    


if __name__ == "__main__":
    db = sql("data/company.db")

    scheme_string = db.get_scheme_string()
    print(scheme_string)

    db.close()
