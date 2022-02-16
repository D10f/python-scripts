from readers import FileReader, YAMLReaderStrategy
from itertools import chain
import constants

class Language:
  
  _language_list = FileReader.read(constants.LANGUAGE_LIST, YAMLReaderStrategy)

  def __init__(self, key):
    self.language = key
    self.data = self._language_list[key]
    

  @classmethod
  def get_language(cls, path):
    match = (
      cls.find_by_filename(path) or
      cls.find_by_extension(path)
    )

    if match:
      return cls(match)

  
  @classmethod
  def get_extensions(cls, key):
    return cls._language_list[key]['extensions']


  @classmethod
  def find_by_filename(cls, path):
    """Searches the list of languages for an exact match based on a filename"""
    filename = path.name
    lang = cls._language_list.get(filename)
    
    # If theres an exact match by filename
    if lang is not None:
      return filename

    for key, value in cls._language_list.items():
      filename_list = value.get('filenames', [])
      if filename in filename_list:
        return key 
    
    return None


  @classmethod
  def find_by_extension(cls, path):
    """Searches the list of languages based on a file extension"""

    # no suffixes typically means .gitignore, Dockerfile, etc...
    # extension = ''.join(path.suffixes) or path.name
    extension = path.suffix or path.name

    for key, value in cls._language_list.items():
      file_ext = value.get('extensions', [])
      file_ali = value.get('aliases', [])

      if extension in chain(file_ext, file_ali):
        return key

    return None