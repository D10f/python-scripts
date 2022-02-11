#!/usr/bin/env python3
 
from pathlib import Path
import yaml

PROJECT_DIR         = Path.cwd()
LANGUAGES_FILE_PATH = Path.joinpath(PROJECT_DIR, 'vendors.yml')

class Language():

  languages: []

  @classmethod
  def load_languages(cls):

    # if self.languages is not None:
    #   return

    with open(LANGUAGES_FILE_PATH) as f:
      languages = yaml.load(f, Loader = yaml.FullLoader)
      print(languages)
      # print(languages['JavaScript'])

# test = Language()

Language.load_languages()
# print(Language.languages())