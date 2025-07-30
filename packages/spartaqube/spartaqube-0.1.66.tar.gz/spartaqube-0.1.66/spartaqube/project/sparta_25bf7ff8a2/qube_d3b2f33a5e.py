import time
from project.logger_config import logger
def sparta_3dac3ff0e9():
	B=0;A=time.time()
	while True:B=A;A=time.time();yield A-B
TicToc=sparta_3dac3ff0e9()
def sparta_fc575492b0(tempBool=True):
	A=next(TicToc)
	if tempBool:logger.debug('Elapsed time: %f seconds.\n'%A);return A
def sparta_e05f1c9dfc():sparta_fc575492b0(False)