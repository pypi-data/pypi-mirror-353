"""file_dat.py

Contains a class that handles dat file IO.
Class is written as an abstract class.
"""

from .file_extension import FileExtension
from pathlib import Path



class DatFile(FileExtension):
    """
    Class that handles dat file IO.

    Attributes
    ----------
    path : pathlib.Path
        absolute path of the file to be managed
    """

    def __init__(self, path: Path) -> None:
        """
        Creates DatFile instance.

        Attributes
        ----------
        path : pathlib.Path
            absolute path of the file to be managed
        """

        super().__init__(path = path, extension_suffix = '.dat')
