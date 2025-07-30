
from pystarburst import Session
import trino.auth
import logging

logging.basicConfig(level=logging.INFO)

class StarburstConnector:
    def __init__(self, host, port, user, password, catalog, schema, http_scheme="https"):
        self.db_parameters = {
            "host": host,
            "port": port,
            "http_scheme": http_scheme,
            "auth": trino.auth.BasicAuthentication(user, password),
            "catalog": catalog,
            "schema": schema
        }
        self.session = None

    def connect(self):
        try:
            self.session = Session.builder.configs(self.db_parameters).create()
            logging.info("Connection successful.")
            return True
        except Exception as e:
            logging.error(f"Connection failed: {str(e)}")
            return False

    def execute_query(self, query):
        if not self.session:
            raise ValueError("Not connected to Starburst. Call connect() first.")
        try:
            result = self.session.sql(query).collect()
            return result
        except Exception as e:
            logging.error(f"Query execution failed: {str(e)}")
            return None
