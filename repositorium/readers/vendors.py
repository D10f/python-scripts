from re import compile

class Vendors:

  def __init__(self, path_to_file, FileReaderStrategy):
    self.path_to_file = path_to_file
    self.file_reader = FileReaderStrategy
    self._vendor_list = None


  @property
  def vendor_list(self):
    if self._vendor_list is None:
      self.compile_list()
    return self._vendor_list


  def compile_list(self):
    """Compiles the list of vendors as regular expressions objects"""
    self._vendor_list = [compile(v) for v in self.file_reader.load(self.path_to_file)]