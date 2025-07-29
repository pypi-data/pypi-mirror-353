"""
# Created : 2025-05-09
# Last Modified : 2025-05-15
# Last Modification :
# Product : bitbucket class/methods
"""

__author__ = ''
__version__ = '0.1.0'
__copyright__ = ''

import requests
from requests.auth import HTTPBasicAuth

from typing import Any, List, Dict
from colorama import Fore, Back, Style

# ----- context manager class -----#
class Bitbucket:
    """ bitbucket class and methods
        REST API:
        https://developer.atlassian.com/cloud/bitbucket/rest/intro/#authentication
    """

    def __init__(self, **kwargs: Any) -> None:

        username            = str(kwargs['USERNAME'])
        app_passwd          = str(kwargs['APP_PWD'])  # read workspace & read repository
        self.workspace      = kwargs['WORKSPACE']
        self.branch         = kwargs['BRANCH']
        self.apiurl         = 'https://api.bitbucket.org/2.0/repositories'

        # client session
        self.session        = requests.Session()
        self.session.auth   = HTTPBasicAuth(username, app_passwd)
        self.session.verify = False  # disable ssl certificate verification
        self.timeout        = (20, 20)  # connect timeout, read timeout

    # ----- get repositories from project
    def get_project_repos(self, project_key: str) -> Dict[Any, Any]:
        """ Get bitbucket repositories from project.

        - Args:
            project_key (str): _description_
        - Api:
            https://api.bitbucket.org/2.0/repositories/brpdigital?q=project.key="GTEL"
        - Returns:
            List[Any]: _description_
        """

        # requests.get(apiurl, auth=HTTPBasicAuth(username, app_password), timeout=20)
        bitbucket_url = f'{self.apiurl}/{self.workspace}'
        params = {
            "q": 'project.key="GTEL"',
            "pagelen": "100"
        }
        response = self.session.get(bitbucket_url, params=params, timeout=self.timeout)

        response.raise_for_status()  # raises an exception if status code is 4xx/5xx

        print(Style.NORMAL + Back.BLACK + Fore.GREEN + f'return repositories from {project_key}')

        j_response = response.json()
        repositories = list(filter(lambda item: item["type"] == "repository", j_response["values"]))
        repos_slug = [item["slug"] for item in j_response["values"]]

        return {
            "repo": repositories,
            "slug": repos_slug
        }

    # ----- return a list of folder(s)
    def get_folders(self, repository: str, folder_path: str) -> List[Any]:
        """ Get bitbucket folders from repository.

        - Args:
            repository (str): _description_
            folder_path: ex. jsonExport/2025-05-08/
        - Api:
            https://api.bitbucket.org/2.0/repositories/brpdigital/<repo>/src/main/
        """

        # requests.get(apiurl, auth=HTTPBasicAuth(username, app_password), timeout=20)
        bitbucket_url = f'{self.apiurl}/{self.workspace}/{repository}/src/{self.branch}/{folder_path}'
        response = self.session.get(bitbucket_url, timeout=self.timeout)

        response.raise_for_status()  # raises an exception if status code is 4xx/5xx

        print(Style.NORMAL + Back.BLACK + Fore.GREEN + f'return folder(s) from {folder_path}')

        j_response = response.json()
        folders = list(filter(lambda item: item["type"] == "commit_directory", j_response["values"]))

        return folders

    # ----- return a list of files
    def get_files(self, repository: str, folder_path: str, file_extention: str) -> List[Any]:
        """ Get json files from jsonfile folder.

        - Args:
            repository (str): _description_
            folder_path: ex. jsonExport/2025-05-08/
            file_extention: ex. json, py etc.
        - Api:
            https://api.bitbucket.org/2.0/repositories/brpdigital/<repo>/src/main/<folder>/
        """

        # requests.get(bitbucket_url, auth=HTTPBasicAuth(username, app_password), timeout=20)
        bitbucket_url = f'{self.apiurl}/{self.workspace}/{repository}/src/{self.branch}/{folder_path}'
        response = self.session.get(bitbucket_url, timeout=self.timeout)

        response.raise_for_status()  # raises an exception if status code is 4xx/5xx

        print(Style.NORMAL + Back.BLACK + Fore.GREEN + f'return {file_extention} file(s) from {folder_path}')

        response.raise_for_status()

        j_response = response.json()
        files = list(filter(lambda item: item["type"] == "commit_file" and item["path"].endswith(f'.{file_extention}'), j_response["values"]))

        return files

    # ----- read file from folder
    def get_file_content(self, repository: str, file_path: str) -> Any:
        """ Get file content from folder.

        - Args:
            repository (str): _description_
            file_path (str): ex. jsonExport/2025-05-08/virtual_machines.json
        - Api:
            https://api.bitbucket.org/2.0/repositories/brpdigital/<repo>/src/main/<file_path>
        """

        bitbucket_url = f'{self.apiurl}/{self.workspace}/{repository}/src/{self.branch}/{file_path}'
        response = self.session.get(bitbucket_url, timeout=self.timeout)

        print(Style.NORMAL + Back.BLACK + Fore.GREEN + f'return content from {file_path}')

        # response.status_code = 200
        response.raise_for_status()

        return response

    # ----- write to file
    def write_to_file(self, repo_slug: str, files: Dict[str, Any]) -> Any:
        """ Write to file in a repository

        - Args:
            repository (str): _description_
            files (str): _description_
        - Api:
            https://api.bitbucket.org/2.0/repositories/brpdigital/<repo>/src
        """

        post_url = f'{self.apiurl}/{self.workspace}/{repo_slug}/src'
        response = self.session.post(post_url, files=files, timeout=self.timeout)

        print(Style.NORMAL + Back.BLACK + Fore.GREEN + f'update version file in {repo_slug}')

        # response.status_code = 201
        response.raise_for_status()

        return response
