""" aionsxt init """
import os

__version__ = '0.0.2'

# libraries path
# C:\Users\richado\AppData\Local\Programs\Python\Python312\Lib\site-packages\
nsxtlib_path = os.path.dirname(os.path.realpath(__file__))
print(f'nsxt aio library version : {__version__}')
print(f'nsxt aio library path    : {nsxtlib_path}')

# import all functions/methods from nsxt_client.py and nsxt_export.py
from .nsxt_client import *
from .nsxt_export import *
