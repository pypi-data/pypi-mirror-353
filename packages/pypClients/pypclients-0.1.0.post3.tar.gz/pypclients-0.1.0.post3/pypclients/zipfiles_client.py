#!/usr/bin/env python3

"""
# Created : 2024-04-08
# Last Modified : 2025-05-09
# Last Modification :
# Product : zip files functions
"""

__author__ = ''
__version__ = '0.1.0'
__copyright__ = ''

import glob
import os
import datetime

from typing import Any, Dict
from zipfile import ZipFile
from colorama import Fore, Back, Style

# ----- zip file class
class Zip:
    """ a class to handle importing parts of VMC NSX-T """

    def __init__(self, **kwargs: Dict[Any, Any]) -> None:
        """
        - *args allows to pass a varying number of -positional arguments-
        - **kwargs allows to pass a varying number of -keyword (or named)-
        - unpacking operator (*) or (**)
        *args (tuple):
            0 = SCRIPT_PATH
            1 = NSX_MGR
            2 = FOLDER
        """

        self.script_path = kwargs['SCRIPT_PATH']
        self.nsx_fqdn = kwargs['NSX_MGR']
        self.folder = "jsonExport"

    # ----- load options from config files
    def purge_json_files(self) -> bool:
        """ removes the json export files before a new export """

        # glob search \\*.json
        # (alias for global) is used to return all file paths that match a specific pattern
        files = glob.glob(f'{self.script_path}\\{self.folder}\\*.json', recursive=True)
        returnval = True
        for file_path in files:
            try:
                os.remove(file_path)
                print(Style.NORMAL + Back.BLACK + Fore.MAGENTA + 'Deleted', file_path)
            except Exception as e:
                print(Style.NORMAL + Back.BLACK + Fore.RED + 'Error deleting', file_path)
                print(str(e))
                returnval = False

        return returnval


    # ----- purge zip files
    def purge_zip_files(self, max_export_history_files: int) -> Any:
        """ Purge old zip files

        - Args:
            max_export_history_files (int): Maximum number of zip files to keep

        - Returns:
            Any: _description_
        """

        if max_export_history_files == -1:
            print('maximum zips configured as unlimited.')
            return True
        retval = True
        files = glob.glob(f'{self.script_path}\\{self.folder}\\*.zip')

        # ----- return the time of last modification
        files.sort(key=os.path.getmtime)
        print(len(files), "zipfiles found with a configured maximum of", max_export_history_files)

        if len(files) > max_export_history_files:
            num_to_purge = len(files) - max_export_history_files
            print('need to purge:', num_to_purge)
            # ----- files[0:num_to_purge] is a slicing notation that specifies a sub-list containing
            # ----- the elements of files from index 0 to index num_to_purge (the first x elements)
            for file in files[0:num_to_purge]:
                try:
                    os.remove(file)
                    print('purged', file)
                except Exception as e:
                    retval = False
                    print('error purging:', file, str(e))
        return retval

    # ----- zip json files
    def zip_json_files(self) -> Any:
        """ creates a zipfile of exported JSON files """
        
        files = glob.glob(f'{self.script_path}\\{self.folder}\\*.json')
        curenttime = datetime.datetime.now()
        # filename example: 2020-12-02_09-57-13_json-export.zip
        filename = f'{self.nsx_fqdn}_{curenttime.strftime("%Y-%m-%d_%H-%M-%S")}_json-export.zip'

        try:
            print(Style.BRIGHT + Back.BLACK + Fore.BLUE + f'\ncreate export zip file name: {filename}')

            zip_path = f'{self.script_path}\\{self.folder}\\{filename}'
            with ZipFile(zip_path, 'w') as zip_file:
                for file in files:
                    zip_file.write(file, os.path.basename(file))
            return filename
        except Exception as e:
            print('error writing zipfile: ', str(e))
            return False
        finally:
            zip_file.close()
