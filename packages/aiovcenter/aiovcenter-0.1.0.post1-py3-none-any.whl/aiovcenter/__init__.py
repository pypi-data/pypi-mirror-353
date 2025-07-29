""" aiovcenter init """
import os

__version__ = '0.0.2'

# libraries path
# C:\Users\richado\AppData\Local\Programs\Python\Python312\Lib\site-packages\
vcslib_path = os.path.dirname(os.path.realpath(__file__))
print(f'vcenter aio library version : {__version__}')
print(f'vcenter aio library path    : {vcslib_path}')

# import all functions/methods from vcs_client.py
from .vcs_client import *
