from abc import ABC, abstractmethod
import yaml
import json

"""
Simple implementation of the strategy pattern to load data from the file system
"""

class FileReaderStrategy(ABC):
  @abstractmethod
  def load(self):
    pass


class YAMLReaderStrategy(FileReaderStrategy):

  loader = yaml.FullLoader

  @classmethod
  def load(cls, path_to_file):
    with open(path_to_file) as f:
      return yaml.load(f, Loader = cls.loader)


class JSONReaderStrategy(FileReaderStrategy):
  @classmethod
  def load(cls, path_to_file):
    with open(path_to_file) as f:
      return json.loads(f)
