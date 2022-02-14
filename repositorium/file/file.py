from pathlib import Path

class FileBlob:

  def __init__(self, path, language_list):
    self._path = path
    print(language_list)
    # self.is_valid = self.validate_file(path, language_list)


  @property
  def path(self):
    return self._path


  @property
  def name(self):
    return self.path.stem.split('.')[0]
  
  
  @property
  def extension(self):
    return ''.join(self.path.suffixes)

  
  @property
  def size(self):
    return Path.stat(self.path).st_size

  
  @property
  def mime(self):
    return mimetypes.guess_type(self._path)


  def validate_file(self, path, language_list):
    for lang in language_list.keys():
      if (lang.get('extensions') and self.extension in lang.get('extensions')) \
        or (lang.get('aliases') and self.name in lang.get('aliases')) \
        or (lang.get('filenames') and self.name in lang.get('filenames')):
        return True
    
    return False