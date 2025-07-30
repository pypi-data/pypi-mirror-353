try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
except:
    pass
import pandas as pd
from project.sparta_6b7c630ead.sparta_e12a2379ef.qube_3f8a709aad import EngineBuilder
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_538e75a6b0 import convert_to_dataframe
from project.logger_config import logger


class MongoConnector(EngineBuilder):

    def __init__(self, host, port, user, password, database):
        """
        
        """
        port = int(port)
        super().__init__(host=host, port=port, user=user, password=password,
            database=database, engine_name='mongodb')
        self.database = database
        self.client = None
        self.connector = self.connect_db()

    def connect_db(self):
        self.client = self.build_mongo()
        return self.client[self.database]

    def test_connection(self) ->bool:
        """
        Test connection
        """
        try:
            client = MongoClient(host=self.host, username=self.user, port=
                self.port, password=self.password, serverSelectionTimeoutMS
                =2000)
            res_ping = client.admin.command('ping')
            databases = client.list_database_names()
            res = False
            if self.database in databases:
                res = True
            self.error_msg_test_connection = (
                f"MongoDB connection is valid but database '{self.database}' does not exist. Available databases are: {', '.join(databases)}"
                )
            client.close()
            return res
        except ConnectionFailure:
            self.error_msg_test_connection = (
                'MongoDB connection test failed: Unable to connect to the server'
                )
            return False
        except Exception as e:
            logger.debug(f'MongoDB connection test failed: {e}')
            self.error_msg_test_connection = str(e)
            return False

    def get_available_tables(self) ->list:
        """
        OVERRIDE engine_builder
        This method returns all the available tables of a database
        """
        try:
            collections = self.connector.list_collection_names()
            self.client.close()
            return collections
        except Exception as e:
            self.client.close()
            logger.debug(f'Failed to list tables: {e}')
            return []

    def get_table_columns(self, table_name) ->list:
        """
        OVERRIDE engine_builder
        This method returns all the available columns of a table
        """
        collection_name = table_name
        sample_size = 100
        try:
            db = self.connector
            collection = db[collection_name]
            documents = collection.find().limit(sample_size)
            field_names = set()
            for doc in documents:
                field_names.update(doc.keys())
            self.client.close()
            return sorted(list(field_names))
        except Exception as e:
            self.client.close()
            logger.debug(
                f"Failed to list columns for table '{table_name}': {e}")
            return []

    def get_data_table(self, table_name) ->pd.DataFrame:
        """
        OVERRIDE engine_builder
        """
        collection_name = table_name
        try:
            db = self.connector
            collection = db[collection_name]
            documents = list(collection.find({}, {'_id': False}))
            self.client.close()
            return convert_to_dataframe(documents)
        except Exception as e:
            self.client.close()
            raise Exception(e)

    def get_data_table_top(self, table_name, top_limit=100) ->pd.DataFrame:
        """
        OVERRIDE engine_builder
        """
        collection_name = table_name
        try:
            db = self.connector
            collection = db[collection_name]
            documents = list(collection.find({}, {'_id': False}).limit(
                top_limit))
            self.client.close()
            return convert_to_dataframe(documents)
        except Exception as e:
            self.client.close()
            raise Exception(e)

    def get_data_table_query(self, sql, table_name=None) ->pd.DataFrame:
        """
        OVERRIDE engine_builder
        """
        try:
            exec(sql, globals(), locals())
            filters_to_apply = eval('filter_criteria')
            collection_name = table_name
            db = self.connector
            collection = db[collection_name]
            documents = list(collection.find(filters_to_apply, {'_id': False}))
            self.client.close()
            return convert_to_dataframe(documents)
        except Exception as e:
            self.client.close()
            raise Exception(e)

#END OF QUBE
