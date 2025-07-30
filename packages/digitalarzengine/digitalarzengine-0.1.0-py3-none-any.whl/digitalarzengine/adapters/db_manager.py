from urllib.parse import quote_plus

from sqlalchemy import create_engine
import geopandas as gpd
import pandas as pd

from digitalarzengine.settings import DATABASES
from digitalarzengine.utils.crypto import CryptoUtils


class DBManager:
    def __init__(self, user: str, password: str, host: str, port: int, dbname: str,
                 driver: str = "postgresql+psycopg2"):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.dbname = dbname
        self.driver = driver
        self._engine = None

    @staticmethod
    def from_config(db_key: str):
        """
            Create a DBManager instance using the `DATABASES` dictionary from a settings module.
            :param db_key: Key in the DATABASES dictionary (e.g., "drm")
            :return: DBManager instance
       """
        db_config = DATABASES[db_key]
        password = CryptoUtils().decrypt_txt(db_config['PASSWORD'])
        return DBManager(
            user=db_config["USER"],
            password=password,
            host=db_config["HOST"],
            port=int(db_config["PORT"]),
            dbname=db_config["NAME"],
            driver=f"{db_config.get('ENGINE', 'postgresql+psycopg2')}"
        )

    def get_sqlalchemy_url(self) -> str:
        user = quote_plus(self.user)
        password = quote_plus(self.password)
        url = f"{self.driver}://{user}:{password}@{self.host}:{self.port}/{self.dbname}"
        return url

    def get_engine(self):
        if self._engine is None:
            self._engine = create_engine(self.get_sqlalchemy_url())
        return self._engine

    def get_geometry_columns(self, table_name: str) -> list:
        """
        Return a list of geometry/geography columns for the given table.

        :param table_name: Table name (e.g., 'my_table' or 'schema.my_table')
        :return: List of column names with geometry/geography types
        """
        engine = self.get_engine()
        if '.' in table_name:
            schema, table = table_name.split('.', 1)
        else:
            schema, table = 'public', table_name

        with engine.connect() as conn:
            result = conn.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = %s
                  AND table_name = %s
                  AND udt_name IN ('geometry', 'geography')
                """, (schema, table)
            )
            return [row[0] for row in result]

    def read_as_geo_dataframe(self, table_name: str = None, geom_col: str = 'geom',
                              query: str = None) -> gpd.GeoDataFrame:
        """
        Read a table or custom SQL query into a GeoDataFrame.

        :param table_name: Name of the table (ignored if `query` is provided)
        :param geom_col: Name of the geometry column
        :param query: Optional SQL query to execute
        :return: GeoDataFrame
        """
        if query is None:
            if not table_name:
                raise ValueError("Either 'table_name' or 'query' must be provided.")
            sql = f"SELECT * FROM {table_name}"
        else:
            sql = query

        return gpd.read_postgis(sql, con=self.get_engine(), geom_col=geom_col)

    def read_as_dataframe(self, table_name: str = None, query: str = None,
                          exclude_geometry: bool = True) -> pd.DataFrame:
        engine = self.get_engine()

        if query is None:
            if not table_name:
                raise ValueError("Either 'table_name' or 'query' must be provided.")
            sql = f"SELECT * FROM {table_name}"
        else:
            sql = query

        df = pd.read_sql(sql, con=engine)

        if exclude_geometry and table_name:
            geom_cols = self.get_geometry_columns(table_name)
            df = df.drop(columns=geom_cols, errors='ignore')

        return df
