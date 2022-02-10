from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class Language(language_file_path):

  self.languages: [str]

  @classmethod()
  def load_languages(cls, path_to_file):
    languages_file = Path(language_file_path).resolve()
    yaml.load(languages_file)