#!/usr/bin/env python3
 
from pathlib import Path
import yaml

MODULE_DIR  = Path.joinpath(Path.cwd(), __name__.split('.')[0])
LANGUAGES_FILE_PATH = Path.joinpath(MODULE_DIR, 'languages.yml')

class Language:

  _languages = None

  @classmethod
  def load_languages(cls):
    """Reads the languages files and updates the internal property"""
    with open(LANGUAGES_FILE_PATH) as f:
      cls._languages = yaml.load(f, Loader = yaml.FullLoader)


  @classmethod
  def get_all_languages(cls):
    """Returns the specified language from the language list"""

    if cls._languages is None:
      cls.load_languages()
    
    return cls._languages


  @classmethod
  def get_language(cls, language):
    """Returns the specified language from the language list"""
    return cls.get_all_languages()[language]