"""file_json.py

Contains a class that handles JSON file IO.
"""

from .file_extension import FileExtension
from lunapyutils import handle_error
import json
from pathlib import Path



class JSONFile(FileExtension):
    """
    Class that handles JSON file IO.

    Attributes
    ----------
    path : pathlib.Path
        absolute path of the file to be managed
    """

    def __init__(self, path : Path) -> None:
        """
        Creates JSONFile instance.

        Attributes
        ----------
        path : pathlib.Path
            absolute path of the file to be managed
        """

        super().__init__(path = path, extension_suffix = '.json')


    def read(self) -> dict | None:
        """
        Opens JSON file and returns its data.

        Returns
        -------
        dict
            the data contained in the file | 
            None is there was an error
        """

        data = None
        try:
            with open(self.path, 'r') as f:
                data = json.load(f)

        except IOError as e:
            handle_error(e, 'JSONFile.open()',
                         'error opening file')

        except Exception as e:
            handle_error(e, 'JSONFile.open()', 
                         'erroneous error opening file')

        finally:
            return data
        

    def write(self, data : dict) -> bool:
        """
        Writes data to JSON file.

        Parameters
        ----------
        data : dict
            the data to write to the file

        Returns
        -------
        bool
            True,  if the data was written to the file |
            False, otherwise
        """

        saved = False
        try: 
            with open(self.path, 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                saved = True
        
        except Exception as e:
            handle_error(e, 'JSONFile.write()', 'error writing to file')

        finally:
            return saved
        

    def print(self) -> None:
        """
        Opens the json file and prints the data.
        """
        
        data = self.read()
        print(json.dumps(data, indent=2))