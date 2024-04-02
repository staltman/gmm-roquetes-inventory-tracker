import streamlit as st
import pandas as pd
import uuid


class SqliteWrapper:
    def __init__(self, conn, table_name, init=True):
        self.conn = conn
        self.table_name = table_name
        if init:
            self.initialise()
            self.fill_with_sample_data()

    def initialise(self):
        """Child classes need to override this method with init actions"""
        raise NotImplementedError("Subclasses must implement the <initialise> method.")

    def column_config(self):
        """
        Columns configuration for the table. Must be defined in child classes
        https://docs.streamlit.io/library/api-reference/data/st.column_config
        """
        raise NotImplementedError("Subclasses must implement the <column_config> method.")

    def sample_data(self):
        return []

    def fill_with_sample_data(self):
        self.add_rows(self.conn.cursor(), self.sample_data())
        self.conn.commit()

    def commit_changes(self):
        """
        Commit changes made in streamlit dataframe
        https://docs.streamlit.io/library/advanced-features/dataframes
        Commit happens only if all changes succeeded
        """

        original_df = self.records()  # Make sure it is always the same as was displayed to the user
        changes = st.session_state[f"{self.table_name}_table"]
        cursor = self.conn.cursor()

        if edited_rows := changes["edited_rows"]:
            for i, row in edited_rows.items():
                row["id"] = original_df.loc[i, "id"]

            self.update_rows(cursor, list(edited_rows.values()))

        if added_rows := changes["added_rows"]:
            self.add_rows(cursor, added_rows)

        if deleted_rows := changes["deleted_rows"]:
            row_ids = [original_df.loc[i, "id"] for i in deleted_rows]
            self.delete_rows(cursor, row_ids)

        st.toast(f"Edited {len(edited_rows)} row(s)") if len(edited_rows) else None
        st.toast(f"Added {len(added_rows)} row(s)") if len(added_rows) else None
        st.toast(f"Deleted {len(deleted_rows)} row(s)") if len(deleted_rows) else None
        self.conn.commit()

    @staticmethod
    def _execute(cursor, sql, params):
        print(sql, params, sep="\n")
        cursor.execute(sql, params)

    @staticmethod
    def _executemany(cursor, sql, params):
        print(sql, params, sep="\n")
        cursor.executemany(sql, params)

    def update_rows(self, cursor, rows):
        """
        Update rows based on row id
        We assume user cannot change id as it is always assigned automatically
        """

        for row in rows:
            sql = f"""
            UPDATE {self.table_name}
            SET
                {", ".join(f"{k} = :{k}" for k in row.keys())}
            WHERE id = :id
            """
            self._execute(cursor, sql, row)

    def add_rows(self, cursor, rows):
        """
        Add new rows
        Function assure each row has a unique id field by auto-generating UUID4 string for each record
        """

        for row in rows:
            row["id"] = str(uuid.uuid4())
            sql = f"""
                INSERT INTO {self.table_name}
                    ({", ".join(row.keys())})
                VALUES
                    ({", ".join(":" + k for k in row.keys())})
                """
            self._execute(cursor, sql, row)

    def delete_rows(self, cursor, row_ids):
        """Delete rows based on row IDs provided"""

        sql = f"DELETE FROM {self.table_name} WHERE id = :id"
        params = [{"id": i} for i in row_ids]
        self._executemany(cursor, sql, params)

    def records(self):
        """
        Returns table records
        TODO: do not use pandas directly here
        """
        return pd.read_sql_query(f"SELECT * FROM {self.table_name}", self.conn)

    def data_editor(self):
        """
        Streamlit data editor object to display table records
        Set up Streamlit session state variable - <table_name>_table
        Adds commit button that commits the changes user has made
        """
        st.data_editor(
            self.records(),
            num_rows="dynamic",  # allow appending/deleting rows
            key=f"{self.table_name}_table",
            column_config=self.column_config()
        )
        st.button(
            f"Commit",
            key=f"commit_{self.table_name}",
            type="primary",
            disabled=not self.has_uncommitted_changes(),
            on_click=self.commit_changes,
        )

    def has_uncommitted_changes(self):
        return any(len(v) for v in st.session_state[f"{self.table_name}_table"].values())
