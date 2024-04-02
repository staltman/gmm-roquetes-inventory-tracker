from lib.db.sqlite_wrapper import SqliteWrapper
from streamlit.column_config import TextColumn


class Warehouses(SqliteWrapper):

    def __init__(self, conn, init=True):
        super().__init__(conn, "warehouses", init)

    def initialise(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warehouses (
                id TEXT PRIMARY KEY NOT NULL,
                name TEXT NOT NULL UNIQUE,
                address TEXT,
                description TEXT,
                comments TEXT
            );""")

        self.conn.commit()

    def column_config(self):
        return {
            "id": TextColumn("ID (autofilled)", disabled=True),  #default=str(uuid.uuid4())),,
            "name": TextColumn("Name", required=True),
            "address": TextColumn("Address", required=True),
            "description": TextColumn("Description"),
            "comments": TextColumn("Comments"),
        }

    def sample_data(self):
        return [
            {"name": "Les Roquetes", "address": "Carrer Eugeni d'Ors", "description": "Main Warehouse"},
        ]
