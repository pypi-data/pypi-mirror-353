import os
from project.sparta_25bf7ff8a2.sparta_adcf490435.qube_013a49b349 import qube_013a49b349
from project.sparta_25bf7ff8a2.sparta_adcf490435.qube_2a0ec0ae7c import qube_2a0ec0ae7c
from project.sparta_25bf7ff8a2.sparta_adcf490435.qube_5919a17daa import qube_5919a17daa
from project.sparta_25bf7ff8a2.sparta_adcf490435.qube_7194208eb5 import qube_7194208eb5
class db_connection:
	def __init__(A,dbType=0):A.dbType=dbType;A.dbCon=None
	def get_db_type(A):return A.dbType
	def getConnection(A):
		if A.dbType==0:
			from django.conf import settings as B
			if B.PLATFORM in['SANDBOX','SANDBOX_MYSQL']:return
			A.dbCon=qube_013a49b349()
		elif A.dbType==1:A.dbCon=qube_2a0ec0ae7c()
		elif A.dbType==2:A.dbCon=qube_5919a17daa()
		elif A.dbType==4:A.dbCon=qube_7194208eb5()
		return A.dbCon