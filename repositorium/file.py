from pathlib import Path
from language import Language

class File:

  def __init__(self, path):
    self._path = path
    self._language = Language.get_language(path)


  @property
  def path(self):
    return self._path


  @property
  def name(self):
    return self._path.name
  

  @property
  def size(self):
    return Path.stat(self.path).st_size


  @property
  def extension(self):
    return self.path.suffix
  
  
  @property
  def extensions(self):
    return Language.get_extensions(self._language.language)


  @property
  def language(self):
    if self._language:
      return self._language.language
    return None


  @property
  def type(self):
    if self._language:
      return self._language.data.get('type', 'N/A')
    return None


  @property
  def color(self):
    if self._language:
      return self._language.data.get('color', 'N/A')
    return None