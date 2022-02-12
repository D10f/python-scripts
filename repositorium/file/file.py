from pathlib import Path

class FileBlob:

  def __init__(self, path):
    self._path = path
    self._name = path.stem.split('.')[0]
    self._extension = ''.join(path.suffixes)
    self._size = Path.stat(path).st_size


  @property
  def size(self):
    return self._size


  @property
  def name(self):
    return self._name
  
  
  @property
  def extension(self):
    return self._extension

