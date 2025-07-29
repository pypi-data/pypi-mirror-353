#!/usr/bin/env python3

"""
# Created : 2024-04-08
# Last Modified : 2025-05-09
# Last Modification :
# Product : sql functions
"""

__author__ = ''
__version__ = '0.1.0'
__copyright__ = ''

import pymssql

from typing import Any
from colorama import Fore, Back, Style

# ----- open/close sql connection
class SqlConnection:
    """
    context manager reference:
    https://www.pythontutorial.net/advanced-python/python-context-managers/
    https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html

    """

    # ----- init variables with 'config' dictionary
    def __init__(self, config: Any) -> None:

        self.config = config
        self.connection = None

    # ----- open database connection
    def __enter__(self) -> None:
        """ create database connection """
        
        print(Style.NORMAL + Back.BLACK + Fore.BLUE + 'opening database connection')

        dbconfig = {
            'server': self.config['server'],
            'user': self.config['user'],
            'password': self.config['password'],
            'database': self.config['database'],
            'port': self.config['port'],
            'as_dict': True,
        }

        self.connection = pymssql.connect(**dbconfig)

        return self.connection

    # ----- close database connection and cleanup
    def __exit__(self, ex_type: Any, ex_value: Any, ex_traceback: Any) -> None:
        """ close database connection and cleanup """

        print(Style.NORMAL + Back.BLACK + Fore.BLUE + 'closing database connection')

        # ----- close connection
        self.connection.close
