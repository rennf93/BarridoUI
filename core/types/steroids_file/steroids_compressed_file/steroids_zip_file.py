import zipfile
import shutil

from core.types.steroids_file.steroids_compressed_file import SteroidsCompressedFilesBaseClass
from core.types.tools.directory_tools import remove_hidden_files, remove_hidden_files_names


class SteroidsZipFile(SteroidsCompressedFilesBaseClass):

    def open(self):
        return zipfile.ZipFile(self.source_file)

    def read(self):
        pass

    def pick(self, target_file_name):
        """

        Args:
            target_file_name (str): Nombre del archivo

        Returns:

        """
        return self.open().open(target_file_name)

    def decompress_file(self, destination_file):
        with open(destination_file, 'wb') as f_out, zipfile.ZipFile(self.source_file) as f_in:
            shutil.copyfileobj(f_in, f_out)

    def decompress_files(self, destination_folder):
        zipfile.ZipFile(self.source_file).extractall(path=destination_folder)

    def get_files(self):
        with zipfile.ZipFile(self.source_file, 'r') as zf:
            return remove_hidden_files(zf.filelist)

    def get_file_list(self):
        return list(self.filter_file_list())
    
    def filter_file_list(self):
        with zipfile.ZipFile(self.source_file, 'r') as zf:
            return remove_hidden_files(zf.namelist())
