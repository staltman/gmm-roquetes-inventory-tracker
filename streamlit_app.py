import streamlit as st
import sqlite3

from pathlib import Path

from lib.db.inventory import Inventory
from lib.db.products import Products
from lib.db.warehouses import Warehouses

# TODO:
#   - user authentication
#     https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
#   - add internal libs to python path
#   - limit choices in column to only available products

st.set_page_config(
    page_title="GMM-Roquetes inventory tracker",
    page_icon=":shopping_bags:",
)


def connect_db():
    DB_NAME = "gmm_inventory_tracker"
    DB_FILENAME = Path(__file__).parent / f"{DB_NAME}.db"

    db_already_exists = DB_FILENAME.exists()
    # Better to use connection for easier swap between engines
    # conn = st.connection(DB_NAME, type="sql")
    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists
    return conn, db_was_just_created


'''
# :shopping_bags: GMM-Roquetes inventory tracker

**Welcome to intentory tracker!**

This page reads and writes directly from/to our inventory database.
'''

st.info('''
    Use the table below to add, remove, and edit items.
    And don't forget to commit your changes when you're done.
    ''')

conn, db_was_just_created = connect_db()

products = Products(conn, db_was_just_created)
warehouses = Warehouses(conn, db_was_just_created)
inventory = Inventory(products, warehouses, conn, db_was_just_created)


st.header("Inventory")
inventory.data_editor()

st.header("Products")
products.data_editor()

st.header("Warehouses")
warehouses.data_editor()


# st.session_state.products_table  # TODO: Delete. For debug purposes.



# st.metric("My metric", 42, 2)
