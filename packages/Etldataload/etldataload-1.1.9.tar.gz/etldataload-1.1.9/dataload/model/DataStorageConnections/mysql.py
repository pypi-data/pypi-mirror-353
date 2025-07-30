import pandas as pd
import dataload.utils.logger as l
import dataload.conf.model.connection as con
import dataload.model.datastorageconnection as src
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

class MYSQLSource(src.DataStorageConnection):
    def __init__(self, source):
        self.logger = l.Logger()

        self.mysql_connect = con.Mysql(
            host=source['HOST'],
            user=source['USER'],
            password=source['PASSWORD'],
            port=source['PORT'],
            database=source['DATABASE']
        )
        self.connection = con.Connection(
            alias=source['ALIAS'],
            type='MYSQL',
            mysql=self.mysql_connect
        )

    def read_data(self, query=None):
        self.logger.debug('lecture de la source MYSQL....')
        engine = None
        try:
            user=self.connection.mysql.user
            password=self.connection.mysql.password
            host=self.connection.mysql.host
            database=self.connection.mysql.database
            db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
            engine = create_engine(db_uri)
            df = pd.read_sql(self.connection.query, engine)
            return df

        except Exception as e:
            print(f"Erreur lors de la lecture de la base de données : {e}")

        finally:
            engine.dispose()

    def write_data(self, df=None, table=None, key_columns=None):
        engine = None
        try:
            user = self.connection.mysql.user
            password = self.connection.mysql.password
            host = self.connection.mysql.host
            database = self.connection.mysql.database

            # Création de l'URI pour SQLAlchemy
            db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
            engine = create_engine(db_uri)

            if df.empty:
                self.logger.info("Le DataFrame d'entrée est vide. Aucune donnée à insérer.")
                print("Le DataFrame d'entrée est vide. Aucune donnée à insérer.")
                return 0

            with engine.begin() as conn:  # <-- `begin()` gère automatiquement le commit
                columns = df.columns.tolist()
                columns_str = ", ".join(columns)
                values_str = ", ".join(["%s"] * len(columns))
                query = f"""
                    INSERT IGNORE INTO {table} ({columns_str})
                    VALUES ({values_str})
                """
                values = [tuple(row) for row in df.to_numpy()]
                result = conn.execute(query, values)
                inserted_rows = result.rowcount

            self.logger.info(f"{inserted_rows} lignes insérées dans la table {table}.")
            print(f"{inserted_rows} lignes insérées dans la table {table}.")
            return inserted_rows

        except SQLAlchemyError as e:
            self.logger.error(f"Erreur lors de l'écriture dans la base de données : {e}")
            print(f"Erreur lors de l'écriture dans la base de données : {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de l'écriture dans la base de données : {e}")
            print(f"Erreur inattendue lors de l'écriture dans la base de données : {e}")
            raise
        finally:
            if engine is not None:
                engine.dispose()
                self.logger.debug("Connexion à la base de données fermée.")