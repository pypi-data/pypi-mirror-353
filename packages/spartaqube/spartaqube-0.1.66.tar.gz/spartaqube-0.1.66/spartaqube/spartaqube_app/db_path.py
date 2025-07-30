import os,sys,getpass,platform
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_e260b12968 import sparta_3d02d75bc2,sparta_1d392443de
def sparta_26c74b1e1b(full_path,b_print=False):
	B=b_print;A=full_path
	try:
		if not os.path.exists(A):
			os.makedirs(A)
			if B:print(f"Folder created successfully at {A}")
		elif B:print(f"Folder already exists at {A}")
	except Exception as C:print(f"An error occurred: {C}")
def sparta_2507ef323f():
	if sparta_1d392443de():A='/app/APPDATA/local_db/db.sqlite3'
	else:C=sparta_3d02d75bc2();B=os.path.join(C,'data');sparta_26c74b1e1b(B);A=os.path.join(B,'db.sqlite3')
	return A