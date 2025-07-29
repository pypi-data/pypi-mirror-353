""" bdfiles init """
import os

__version__ = '0.0.1'

# ----- libraries path
# ----- C:\Users\richado\AppData\Local\Programs\Python\Python312\Lib\site-packages\
lib_path = os.path.dirname(os.path.realpath(__file__))
print(f'clients library version : {__version__}')
print(f'clients library path    : {lib_path}')

# ----- import all functions/methods from files_client.py, sql_client and zipfiles_client
from .bitbucket_client import *
from .files_client import *
from .sql_client import *
from .zipfiles_client import *
