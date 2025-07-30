import os
from project.sparta_25bf7ff8a2.sparta_adcf490435.qube_2a0ec0ae7c import qube_2a0ec0ae7c
from project.sparta_25bf7ff8a2.sparta_adcf490435.qube_013a49b349 import qube_013a49b349
from project.logger_config import logger
class db_custom_connection:
	def __init__(A):A.dbCon=None;A.dbIdManager='';A.spartAppId=''
	def setSettingsSqlite(B,dbId,dbLocalPath,dbFileNameWithExtension):G='spartApp';E=dbLocalPath;C=dbId;from bqm import settings as F,settingsLocalDesktop as H;B.dbType=0;B.spartAppId=C;A={};A['id']=C;A['ENGINE']='django.db.backends.sqlite3';A['NAME']=str(E)+'/'+str(dbFileNameWithExtension);A['USER']='';A['PASSWORD']='2change';A['HOST']='';A['PORT']='';F.DATABASES[C]=A;H.DATABASES[C]=A;D=qube_013a49b349();D.setPath(E);D.setDbName(G);B.dbCon=D;B.dbIdManager=G;logger.debug(F.DATABASES)
	def getConnection(A):return A.dbCon
	def setAuthDB(A,authDB):A.dbType=authDB.dbType