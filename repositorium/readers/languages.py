class Languages:

  def __init__(self, path_to_file, FileReaderStrategy):
    self._language_list = None
    self.path_to_file = path_to_file
    self.file_reader = FileReaderStrategy


  @property
  def language_list(self):
    if self._language_list is None:
      self.load_languages()
    return self._language_list


  def load_languages(self):
    """Reads the languages files and updates the internal property"""
    self._language_list = self.file_reader.load(self.path_to_file)


  def get_language_by_name(self, language_name):
    """Finds a language from the list by its name"""
    return self.language_list[language_name]


  def get_language_by_extension(self, extensions):
    """Finds a language from the list matching the extensions provided"""
    for lang in self.language_list:
      if not lang.get('extensions'):
        continue

      for ext in extensions:
        if ext in lang['extensions']:
          return self.language_list[ext]
  
  
  def get_language_by_alias(self, aliases):
    """Finds a language from the list matching the aliases provided"""
    for lang in self.aliases:
      if not lang.get('extensions'):
        continue

        for ext in extensions:
          if ext in lang['extensions']:
            return self.aliases[ext]