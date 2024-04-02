from streamlit.column_config import TextColumn

from lib.db.sqlite_wrapper import SqliteWrapper


class Products(SqliteWrapper):

    def __init__(self, conn, init=True):
        super().__init__(conn, "products", init)

    def initialise(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY NOT NULL,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                comments TEXT);""")

        self.conn.commit()

    def column_config(self):
        return {
            "id": TextColumn("ID (autofilled)", disabled=True),  #default=str(uuid.uuid4())),
            "name": TextColumn("Name", required=True),
            "description": TextColumn("Description"),
            "comments": TextColumn("Comments"),
        }

    def sample_data(self):
        return [
            {"name": "Product 1", "description": "The First Products"},
            {"name": "Product 2", "description": "The Second Products"},
            {"name": "Product 3", "description": "The Third Products"},
        ]