from streamlit.column_config import TextColumn, SelectboxColumn, NumberColumn

from lib.db.sqlite_wrapper import SqliteWrapper


class Inventory(SqliteWrapper):

    def __init__(self, products, warehouses, conn, init=True):
        super().__init__(conn, "inventory", init)
        self.products = products
        self.warehouses = warehouses

    def initialise(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER NOT NULL,
                warehouse_name TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 0 ,
                PRIMARY KEY (warehouse_name, product_name),
                FOREIGN KEY (warehouse_name)
                    REFERENCES warehouses (name)
                        ON DELETE CASCADE
                        ON UPDATE NO ACTION,
                FOREIGN KEY (product_name)
                    REFERENCES products (name)
                        ON DELETE CASCADE
                        ON UPDATE NO ACTION
            );""")

        self.conn.commit()

    def column_config(self):
        warehouse_options = self.warehouses.records()["name"].tolist()
        product_options = self.products.records()["name"].tolist()
        return {
            "id": TextColumn(
                "ID (autofilled)",
                # default=str(uuid.uuid4()
                disabled=True),
            "warehouse_name": SelectboxColumn(
                "Warehouse",
                required=True,
                options=warehouse_options,
                default=None if not warehouse_options else warehouse_options[0]),
            "product_name": SelectboxColumn(
                "Product",
                required=True,
                options=product_options,
                default=None if not product_options else product_options[0]),
            "quantity": NumberColumn(
                "Comments",
                required=True,
                default=0,
                min_value=0,
                max_value=999999,  # if we are above this we are millionaires
            ),
        }
