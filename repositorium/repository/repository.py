#!/usr/bin/env python3

from pathlib import Path
import subprocess
import sys

from logger.logger import Logger
# from languages.languages import Language

class Repository:

  def __init__(self, git_path, branch):
    self.logger = Logger.create_logger(__name__)
    self.git_root_dir(git_path.resolve(), branch = branch)


  @property
  def entrypoint(self):
    return self._entrypoint
  

  @entrypoint.setter
  def entrypoint(self, new_path):
    self.logger.info(f'Git entrypoint: {new_path}')
    self._entrypoint = new_path


  @property
  def branch(self):
    return self._branch
  

  @branch.setter
  def branch(self, new_branch):
    self.logger.info(f'Checked-out branch: {new_branch}')
    self._branch = new_branch


  @property
  def gitignore(self):
    return self.gitignore_list()


  @gitignore.setter
  def gitignore(self, new_list):
    self.logger.debug(f'Using .gitignore file with {len(new_list)} entries')
    self._gitignore = new_list


  @property
  def size(self):
    return self._size

  
  @size.setter
  def size(self, new_size):
    self._size = new_size


  def git_root_dir(self, git_path, branch = None):
    """Verifies and changes directories to the root of the git repo"""

    # TODO: Allow to specify branch

    res = subprocess.run(
      ['git', 'rev-parse', '--show-toplevel', '--abbrev-ref', 'HEAD'],
      capture_output=True,
      cwd=git_path
    )

    if res.returncode == 128:
      self.logger.warning(f'Not a git repository (or any of the parent directories): {git_path}')
      sys.exit(res.returncode)

    if res.returncode > 0:
      self.logger.error(res.stderr.decode('UTF-8'))
      sys.exit(res.returncode)

    root_dir, branch = res.stdout.decode('UTF-8').strip().split('\n')

    self.entrypoint = root_dir
    self.branch = branch

  
  def get_files(self, *ignore_list):
    """Returns a list of all files that pass the following exclusion rules:
      1. Exclude if found in .gitignore file
      2. Exclude dir paths matching known vendors, bundlers, package managers, etc.
      3. Exclude files matching known vendors, config, metadata, libraries, etc.
      4. Exclude files with non-programming extensions and binary formats.
    """

    for current_dir, dirnames, filenames in os.walk(self.entrypoint):

      dirnames[:] = [d for d in dirnames if d not in itertools.chain(ignore_list, self.gitignore)]

      for f in filenames:
        if f in itertools.chain(ignore_list, self.gitignore):
          continue
        yield Path.joinpath(Path(current_dir), f)

  
  def gitignore_list(self):
    """Checks for the presence of a .gitignore file and returns it as a list"""

    # TODO: use proper git built-in commands to extract info from commits

    if self._gitignore is not None:
      return self._gitignore

    # always ignore .git directory
    result = ['.git']

    gitignore_file = Path.joinpath(self.entrypoint, '.gitignore')

    if not Path.exists(gitignore_file):
      self._gitignore = result
    else:
      with open(gitignore_file) as file:
        result.extend([line.rstrip('/\n') for line in file.readlines() if line != '\n'])
        self._gitignore = result
