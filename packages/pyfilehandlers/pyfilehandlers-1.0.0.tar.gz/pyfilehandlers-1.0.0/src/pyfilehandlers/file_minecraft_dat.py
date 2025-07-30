"""file_minecraft_dat.py

Contains a class that handles Minecraft dat file IO.
"""

from .file_dat import DatFile
from lunapyutils import handle_error
import amulet_nbt
from pathlib import Path

from amulet_nbt import NamedTag



class DatFile(DatFile):
    """
    Class that handles Minecraft dat file IO.

    Attributes
    ----------
    path : pathlib.Path
        absolute path of the file to be managed
    """

    def __init__(self, path: Path) -> None:
        """
        Creates MinecraftDatFile instance.

        Attributes
        ----------
        path : pathlib.Path
            absolute path of the file to be managed
        """

        super().__init__(path = path, extension_suffix = '.dat')


    def read(self) -> NamedTag | None:
        """
        Opens Minecraft dat file and returns its data.

        Returns
        -------
        amulet_nbt.NamedTag
            the data contained in the file | 
            None is there was an error
        """

        data = None
        try:
            data : NamedTag = amulet_nbt.load(self.path)

        except IOError as e:
            handle_error(e, 'MinecraftDatFile.open()',
                         'error opening file')

        except Exception as e:
            handle_error(e, 'MinecraftDatFile.open()', 
                         'erroneous error opening file')

        finally:
            return data
        

    def write(self, data: NamedTag) -> bool:
        """
        Writes data to Minecraft dat file. Overwrites all data held in file.

        Parameters
        ----------
        data : amulet_nbt.NamedTag
            the data to write to the file

        Returns
        -------
        bool
            True,  if the data was written to the file |
            False, otherwise
        """

        saved = False
        try: 
            data.save_to(self.path)
            saved = True
        
        except Exception as e:
            handle_error(e, 'MinecraftDatFile.write()', 'error writing to file')

        finally:
            return saved
        
    
    def print(self) -> None:
        """
        Opens the Minecraft dat file and prints the data.
        """
        
        data = self.read()
        print(data)