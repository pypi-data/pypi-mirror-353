"""
Copyright 2024-2025 Aplos Analytics
All Rights Reserved.   www.aplosanalytics.com   LICENSED MATERIALS
Property of Aplos Analytics, Utah, USA
"""

import os
from pathlib import Path
from typing import List

from aplos_nca_saas_sdk.utilities.environment_services import EnvironmentServices


class FileUtility:
    """General File Utilities"""

    @staticmethod
    def load_filepath(file_path: str) -> str:
        """Load the file_path"""
        if not file_path:
            raise RuntimeError("file_path is required")
        elif file_path.startswith("${module}"):
            # find the path
            es: EnvironmentServices = EnvironmentServices()
            root = es.find_module_path()
            if not root:
                raise RuntimeError(
                    "Unable to find the module path.  Please use the ${module} syntax to define the file path"
                )
            file_path = file_path.replace("${module}", root)

        # get the correct os path separator
        file_path = os.path.normpath(file_path)
        return file_path


    def find_file(
        self, starting_path: str, file_name: str, raise_error_if_not_found: bool = True
    ) -> str | None:
        """Searches the project directory structure for a file"""
        
        starting_path = starting_path or __file__
        parents = len(starting_path.split(os.sep)) -1
        paths: List[str] = []
        for parent in range(parents):
            try:
                path = Path(starting_path).parents[parent].absolute()

                tmp = os.path.join(path, file_name)
                paths.append(tmp)
                if os.path.exists(tmp):
                    return tmp
            except Exception as e:
                print(f"Error {str(e)}")
                print(f"Failed to find the file: {file_name}.")
                print(f'Searched: {"\n".join(path)}.')
                                

        if raise_error_if_not_found:
            searched_paths = "\n".join(paths)
            raise RuntimeError(
                f"Failed to locate environment file: {file_name} in: \n {searched_paths}"
            )

        return None