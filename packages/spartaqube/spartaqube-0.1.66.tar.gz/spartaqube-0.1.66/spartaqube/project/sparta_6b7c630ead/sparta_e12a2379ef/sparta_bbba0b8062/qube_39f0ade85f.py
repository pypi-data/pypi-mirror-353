import time
from project.sparta_6b7c630ead.sparta_e12a2379ef.qube_3f8a709aad import EngineBuilder
from project.logger_config import logger


class MysqlConnector(EngineBuilder):

    def __init__(self, host, port, user, password, database):
        """
        
        """
        super().__init__(host=host, port=port, user=user, password=password,
            database=database, engine_name='mysql')
        self.connector = self.connect_db()

    def connect_db(self):
        return self.build_mysql()

    def test_connection(self) ->bool:
        """
        Test connection
        """
        try:
            if self.connector.is_connected():
                self.connector.close()
                return True
            else:
                return False
        except Exception as e:
            logger.debug(f'Error: {e}')
            return False

#END OF QUBE
