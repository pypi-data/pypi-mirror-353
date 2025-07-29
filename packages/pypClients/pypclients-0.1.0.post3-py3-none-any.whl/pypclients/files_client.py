#!/usr/bin/env python3

"""
# Created : 2024-04-08
# Last Modified : 2025-05-09
# Last Modification :
# Description : files functions
"""

__author__ = ''
__version__ = '0.1.0'
__copyright__ = ''

import json
import hcl2
import pandas as pd

from typing import Optional, Any, IO, TextIO
from colorama import Fore, Back, Style

# ----- files manager class
class OpenFile:
    """
    context manager reference:
    https://www.pythontutorial.net/advanced-python/python-context-managers/
    https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html

    NOTE: this class replace "try except finally" from read_terrafile function
    """

    def __init__(self,
                 filename: str,
                 mode: str,
                 file_type: str,
                 output: Optional[Any] = None,
                 seprator: Optional[Any] = None,
                 xlsheet: Optional[Any] = None,
                 xlcol: Optional[Any] = None
                 ) -> None:

        self.filename = filename
        self.mode = mode  # read, write
        self.type = file_type  # file extention: csv, xlsx, etc
        self.separator = seprator  # csv separator ',' ';' etc
        self.output = output
        self.xlsheet = xlsheet
        self.xlcol = xlcol
        #self.filehandle: Optional[Union[IO[Any], TextIO]] = None
        self.filehandle: Optional[IO[Any] | TextIO]

    # ----- setup the context and optionally return some object
    def __enter__(self) -> Any:
        print(Style.NORMAL + Back.BLACK + Fore.BLUE + f'opening the file {self.filename}')

        try:
            # open file
            if self.type == 'xlsx':
                # xlsx files
                self.filehandle = open(self.filename, self.mode, newline='')
            else:
                # other files
                self.filehandle = open(self.filename, self.mode)
        except FileNotFoundError as e:
            print(Style.NORMAL + Back.BLACK + Fore.RED + f'file not found : {self.filename}')
            raise ValueError('file not found') from e  # raise Exception(FileNotFoundError)
        except IOError as e:  # IOError is OSError
            print(Style.NORMAL + Back.BLACK + Fore.RED + f'I/O error for file : {self.filename}')
            raise ValueError('io error') from e
        except Exception as e:
            print(Style.NORMAL + Back.BLACK + Fore.RED + f'unexpected error for file : {self.filename}')
            raise ValueError('exception error') from e  # raise Exception(e)
        else:
            # read json file
            if self.type == 'json' and self.mode == 'r':
                return json.load(self.filehandle)
            # write to json file
            elif self.type == 'json' and self.mode == 'w':
                json.dump(self.output, self.filehandle, indent=4)
            # read terraform file
            elif self.type == 'terraform' and self.mode == 'r':
                return hcl2.load(self.filehandle)
            # read csv file
            elif self.type == 'csv' and self.mode == 'r' and self.separator:
                pd.options.display.max_rows = 9999
                # delimiter ';' create a list and header at the first row
                return pd.read_csv(self.filehandle, sep=self.separator, header=0)
            # write to csv file
            elif self.type == 'csv' and self.mode == 'w':
                # index=False ensures dataframe's index is not written to the csv file
                df = pd.DataFrame(self.output)
                df.to_csv(self.filehandle, sep=';', index=False, header=False)
            # read xlsx file
            elif self.type == 'xlsx' and self.mode == 'r':
                return pd.read_excel(self.filehandle.name, sheet_name=self.xlsheet, usecols=self.xlcol)

        return None

    # ----- cleanup the object
    def __exit__(self, ex_type: Any, ex_value: Any, ex_traceback: Any) -> None:
        print(Style.NORMAL + Back.BLACK + Fore.BLUE + f'closing the file {self.filename}')
        # close file
        self.filehandle.close()

    # =============================================#
    # ----- read and return json file contain -----#
    def read_json_file(self) -> Any:
        """read json file"""

        # open and read file
        try:
            # open json file
            # jsonfile = self.import_path+'\\'+self.import_folder+'\\'+filename
            with open(self.filename) as filehandle:
                # returns JSON object as a list/list of dictionaries
                result = json.load(filehandle)
        except Exception:
            print(Style.NORMAL + Back.BLACK + Fore.RED + 'Import failed - unable to open', self.filename)
            return False
        # close file always executed even with an error event
        finally:
            filehandle.close()

        return result
