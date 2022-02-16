from abc import ABC, abstractmethod
from re import compile
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
  @classmethod
  def load(cls, path_to_file, loader = yaml.FullLoader):
    with open(path_to_file) as f:
      return yaml.load(f, Loader = loader)


class JSONReaderStrategy(FileReaderStrategy):
  @classmethod
  def load(cls, path_to_file):
    with open(path_to_file) as f:
      return json.loads(f)


class FileReader:

  """Reads a file in the format specified by the strategy"""

  _read_files = {}

  @classmethod
  def read(cls, path_to_file, reader_strategy):
    if cls._read_files.get(path_to_file.name) is None:
      cls._read_files[path_to_file.name] = reader_strategy.load(path_to_file)
    return cls._read_files.get(path_to_file.name)
