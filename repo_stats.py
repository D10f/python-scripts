#!/usr/bin/env python3

'''
repo_stats.py - Get statistics about your your project such as lines  of code,
number of files, total size, most common programming language used, etc.
'''

from pathlib import Path
import subprocess
import argparse
import logging
import json
import sys
import os

CURRENT_VERSION = 'v0.0.1'

# DEFEAULT PROGRAMMING LANGUAGE FILE EXTENSIONS
# https://gist.github.com/ppisarczyk/43962d06686722d26d176fad46879d41

# FILE_EXTENSIONS = json.loads('file_extensions.json')
FILE_EXTENSIONS = ['.abap', '.asc', '.ash', '.ampl', '.mod', '.g4', '.apl', '.dyalog', '.asp', '.asax', '.ascx', '.ashx', '.asmx', '.aspx', '.axd', '.dats', '.hats', '.sats', '.as', '.adb', '.ada', '.ads', '.agda', '.als', '.cls', '.applescript', '.scpt', '.arc', '.ino', '.aj', '.asm', '.a51', '.inc', '.nasm', '.aug', '.ahk', '.ahkl', '.au3', '.awk', '.auk', '.gawk', '.mawk', '.nawk', '.bat', '.cmd', '.befunge', '.bison', '.bb', '.bb', '.decls', '.bmx', '.bsv', '.boo', '.b', '.bf', '.brs', '.bro', '.c', '.cats', '.h', '.idc', '.w', '.cs', '.cake', '.cshtml', '.csx', '.cpp', '.c++', '.cc', '.cp', '.cxx', '.h', '.h++', '.hh', '.hpp', '.hxx', '.inc', '.inl', '.ipp', '.tcc', '.tpp', '.chs', '.clp', '.cmake', '.cmake.in', '.cob', '.cbl', '.ccp', '.cobol', '.cpy', '.capnp', '.mss', '.ceylon', '.chpl', '.ch', '.ck', '.cirru', '.clw', '.icl', '.dcl', '.click', '.clj', '.boot', '.cl2', '.cljc', '.cljs', '.cljs.hl', '.cljscm', '.cljx', '.hic', '.coffee', '._coffee', '.cake', '.cjsx', '.cson', '.iced', '.cfm', '.cfml', '.cfc', '.lisp', '.asd', '.cl', '.l', '.lsp', '.ny', '.podsl', '.sexp', '.cp', '.cps', '.cl', '.coq', '.v', '.cr', '.feature', '.cu', '.cuh', '.cy', '.pyx', '.pxd', '.pxi', '.d', '.di', '.com', '.dm', '.d', '.dart', '.djs', '.dylan', '.dyl', '.intr', '.lid', '.E', '.ecl', '.eclxml', '.ecl', '.e', '.ex', '.exs', '.elm', '.el', '.emacs', '.emacs.desktop', '.em', '.emberscript', '.erl', '.es', '.escript', '.hrl', '.xrl', '.yrl', '.fs', '.fsi', '.fsx', '.fx', '.flux', '.f90', '.f', '.f03', '.f08', '.f77', '.f95', '.for', '.fpp', '.factor', '.fy', '.fancypack', '.fan', '.fs', '.fth', '.4th', '.f', '.for', '.forth', '.fr', '.frt', '.fs', '.ftl', '.fr', '.gms', '.g', '.gap', '.gd', '.gi', '.tst', '.s', '.ms', '.gd', '.glsl', '.fp', '.frag', '.frg', '.fs', '.fsh', '.fshader', '.geo', '.geom', '.glslv', '.gshader', '.shader', '.vert', '.vrx', '.vsh', '.vshader', '.gml', '.kid', '.ebuild', '.eclass', '.glf', '.gp', '.gnu', '.gnuplot', '.plot', '.plt', '.go', '.golo', '.gs', '.gst', '.gsx', '.vark', '.grace', '.gf', '.groovy', '.grt', '.gtpl', '.gvy', '.gsp', '.hcl', '.tf', '.hlsl', '.fx', '.fxh', '.hlsli', '.hh', '.php', '.hb', '.hs', '.hsc', '.hx', '.hxsl', '.hy', '.bf', '.pro', '.dlm', '.ipf', '.idr', '.lidr', '.ni', '.i7x', '.iss', '.io', '.ik', '.thy', '.ijs', '.flex', '.jflex', '.jq', '.jsx', '.j', '.java', '.jsp', '.js', '._js', '.bones', '.es', '.es6', '.frag', '.gs', '.jake', '.jsb', '.jscad', '.jsfl', '.jsm', '.jss', '.njs', '.pac', '.sjs', '.ssjs', '.sublime-build', '.sublime-commands', '.sublime-completions', '.sublime-keymap', '.sublime-macro', '.sublime-menu', '.sublime-mousemap', '.sublime-project', '.sublime-settings', '.sublime-theme', '.sublime-workspace', '.sublime_metrics', '.sublime_session', '.xsjs', '.xsjslib', '.jl', '.krl', '.sch', '.brd', '.kicad_pcb', '.kt', '.ktm', '.kts', '.lfe', '.ll', '.lol', '.lsl', '.lslp', '.lvproj', '.lasso', '.las', '.lasso8', '.lasso9', '.ldml', '.lean', '.hlean', '.l', '.lex', '.ly', '.ily', '.b', '.m', '.lagda', '.litcoffee', '.lhs', '.ls', '._ls', '.xm', '.x', '.xi', '.lgt', '.logtalk', '.lookml', '.ls', '.lua', '.fcgi', '.nse', '.pd_lua', '.rbxs', '.wlua', '.mumps', '.m', '.m4', '.m4', '.ms', '.mcr', '.muf', '.m', '.mak', '.d', '.mk', '.mkfile', '.mako', '.mao', '.mathematica', '.cdf', '.m', '.ma', '.mt', '.nb', '.nbp', '.wl', '.wlt', '.matlab', '.m', '.maxpat', '.maxhelp', '.maxproj', '.mxt', '.pat', '.m', '.moo', '.metal', '.minid', '.druby', '.duby', '.mir', '.mirah', '.mo', '.mod', '.mms', '.mmk', '.monkey', '.moo', '.moon', '.myt', '.ncl', '.nsi', '.nsh', '.n', '.axs', '.axi', '.axs.erb', '.axi.erb', '.nlogo', '.nl', '.lisp', '.lsp', '.nim', '.nimrod', '.nit', '.nix', '.nu', '.numpy', '.numpyw', '.numsc', '.ml', '.eliom', '.eliomi', '.ml4', '.mli', '.mll', '.mly', '.m', '.h', '.mm', '.j', '.sj', '.omgrofl', '.opa', '.opal', '.cl', '.opencl', '.p', '.cls', '.scad', '.ox', '.oxh', '.oxo', '.oxygene', '.oz', '.pwn', '.inc', '.php', '.aw', '.ctp', '.fcgi', '.inc', '.php3', '.php4', '.php5', '.phps', '.phpt', '.pls', '.pck', '.pkb', '.pks', '.plb', '.plsql', '.sql', '.sql', '.pov', '.inc', '.pan', '.psc', '.parrot', '.pasm', '.pir', '.pas', '.dfm', '.dpr', '.inc', '.lpr', '.pp', '.pl', '.al', '.cgi', '.fcgi', '.perl', '.ph', '.plx', '.pm', '.pod', '.psgi', '.t', '.6pl', '.6pm', '.nqp', '.p6', '.p6l', '.p6m', '.pl', '.pl6', '.pm', '.pm6', '.t', '.l', '.pig', '.pike', '.pmod', '.pogo', '.pony', '.ps1', '.psd1', '.psm1', '.pde', '.pl', '.pro', '.prolog', '.yap', '.spin', '.pp', '.pd', '.pb', '.pbi', '.purs', '.py', '.bzl', '.cgi', '.fcgi', '.gyp', '.lmi', '.pyde', '.pyp', '.pyt', '.pyw', '.rpy', '.tac', '.wsgi', '.xpy', '.qml', '.qbs', '.pro', '.pri', '.r', '.rd', '.rsx', '.rbbas', '.rbfrm', '.rbmnu', '.rbres', '.rbtbar', '.rbuistate', '.rkt', '.rktd', '.rktl', '.scrbl', '.rl', '.reb', '.r', '.r2', '.r3', '.rebol', '.red', '.reds', '.cw', '.rpy', '.rs', '.rsh', '.robot', '.rg', '.rb', '.builder', '.fcgi', '.gemspec', '.god', '.irbrc', '.jbuilder', '.mspec', '.pluginspec', '.podspec', '.rabl', '.rake', '.rbuild', '.rbw', '.rbx', '.ru', '.ruby', '.thor', '.watchr', '.rs', '.rs.in', '.sas', '.smt2', '.smt', '.sqf', '.hqf', '.sql', '.db2', '.sage', '.sagews', '.sls', '.scala', '.sbt', '.sc', '.scm', '.sld', '.sls', '.sps', '.ss', '.sci', '.sce', '.tst', '.self', '.sh', '.bash', '.bats', '.cgi', '.command', '.fcgi', '.ksh', '.sh.in', '.tmux', '.tool', '.zsh', '.sh-session', '.shen', '.sl', '.smali', '.st', '.cs', '.tpl', '.sp', '.inc', '.sma', '.nut', '.stan', '.ML', '.fun', '.sig', '.sml', '.do', '.ado', '.doh', '.ihlp', '.mata', '.matah', '.sthlp', '.sc', '.scd', '.swift', '.sv', '.svh', '.vh', '.txl', '.tcl', '.adp', '.tm', '.tcsh', '.csh', '.t', '.thrift', '.t', '.tu', '.ts', '.tsx', '.upc', '.uno', '.uc', '.ur', '.urs', '.vcl', '.vhdl', '.vhd', '.vhf', '.vhi', '.vho', '.vhs', '.vht', '.vhw', '.vala', '.vapi', '.v', '.veo', '.vim', '.vb', '.bas', '.cls', '.frm', '.frx', '.vba', '.vbhtml', '.vbs', '.volt', '.webidl', '.x10', '.xc', '.xsp-config', '.xsp.metadata', '.xpl', '.xproc', '.xquery', '.xq', '.xql', '.xqm', '.xqy', '.xs', '.xslt', '.xsl', '.xojo_code', '.xojo_menu', '.xojo_report', '.xojo_script', '.xojo_toolbar', '.xojo_window', '.xtend', '.y', '.yacc', '.yy', '.zep', '.zimpl', '.zmpl', '.zpl', '.ec', '.eh', '.fish', '.mu', '.nc', '.ooc', '.wisp', '.prg', '.ch', '.prw']

def main():
  args = parse_arguments()
  start_logger(args.verbose)
  print_arguments(args)

  if args.git_path:
    get_local_repository(args.git_path, args.branch)
  elif args.git_url:
    fetch_remote_repository(args.git_url, args.branch)
  elif args.username:
    fetch_user_data(
      args.username,
      from_provider=args.provider,
      omit_repos=args.omit_repos,
      use_repos=args.use_repos
    )


def get_local_repository(path_to_repo, branch):
  """Searches for and uses a repository in the local machine to run stats for."""

  entrypoint = Path(path_to_repo).resolve()
  is_git_repository = '.git' in [x.name for x in Path.iterdir(entrypoint)]

  if not is_git_repository:
    logger.warning(f'No git repository found in "{entrypoint}"')
    sys.exit(1)

  if not branch_exist(branch, path_to_repo):
    logger.warning(f'No git branch "{branch}" found in "{entrypoint}". Exiting...')
    sys.exit(1)

  ignorefiles = use_ignorefile(path_to_repo)
  
  if ignorefiles:
    logger.debug(f'.gitignore file found ({len(ignorefiles)} lines).')
  
  repo_files = select_files(path_to_repo, ignorefiles)
  
  result = count_lines_of_code(repo_files)

  print(len(repo_files))
  print(result)

  # count lines of code per extension (js, ts, css, etc)
  # calculate top used languages in %

# def fetch_remote_repository(url, branch):
#   pass
# def fetch_user_data(username, from_provider = None, omit_repos = None, use_repos = None):
#   pass


def count_lines_of_code(files):
  """Counts total lines of code from provided list of files and arranges them
  by file extension in a dictionary.
  """
  lines_by_extension = {}

  for file in files:
    ext = file.suffix

    lines_by_extension.setdefault(ext, 0)

    with open(file, 'rb') as f:
      lines_by_extension[ext] = lines_by_extension[ext] + sum(1 for _ in f)

  return lines_by_extension


def select_files(path_to_repo, ignorefiles):
  """Selects all the files in the given path, recursively."""
  
  result = []

  for current_dir, dirnames, filenames in os.walk(path_to_repo):

    # Prune directories and files listed under ignorefiles
    dirnames[:] = [d for d in dirnames if d not in ignorefiles]

    # Exclude files listed under ignorefiles
    filtered_files = [f for f in filenames if f not in ignorefiles]

    result.extend([Path.joinpath(Path(current_dir), Path(f)) for f in filtered_files])
  
  return result


def use_ignorefile(path_to_repo):
  """Checks for the presence of a .gitignore file in the specified directory
  and returns it as a list with every entry."""

  gitignore_file = Path.joinpath(path_to_repo, '.gitignore')

  # always ignore .git directory
  result = ['.git']

  if not Path.exists(gitignore_file):
    return result

  with open(gitignore_file) as file:
    result.extend([line.rstrip('/\n') for line in file.readlines() if line != '\n'])
  
  return result
  

def branch_exist(branch_name, path_to_repo):
  """Checks if branch_name exists in the specified git repository"""

  try:
    res = subprocess.run(['git', 'branch', '--list', branch_name], capture_output=True, cwd=path_to_repo)
    return res.stdout
  except Exception as err:
    logger.error(err)
    sys.exit(err.args[0])


def start_logger(verbosity):
  """Starts a new logger instance and configures it based on the verbosity argument"""
  
  stdout_handler = logging.StreamHandler()
  if verbosity == 1:
    logger.setLevel(logging.INFO)
  elif verbosity == 2:
    logger.setLevel(logging.DEBUG)

  # Define formatter for the handler
  fmt = '%(asctime)s [ %(levelname)s ] %(message)s'

  stdout_handler.setFormatter(CustomFormatter(fmt))
  logger.addHandler(stdout_handler)


def print_arguments(args):
  """Prints the arguments used to run the script."""
  
  logger.debug(f'Running with arguments: {args}')

  if args.git_path:
    logger.info(f'Searching repository at location: {args.git_path.resolve()} ({args.branch})')
  
  if args.git_url:
    logger.info(f'Fetching repository url: {args.git_path} ({args.branch})')

  if args.username:
    logger.info(f'Searching for username {args.username} on {args.provider}')

    if args.omit_repos:
      logger.info(f'Ignoring repositories from search: {"".join(args.omit_repos)}')

    if args.use_repos:
      logger.info(f'Searching for reposi repositories from search: {"".join(args.omit_repos)}')
  

def parse_arguments():
  """Parses command line arguments passed to run the script"""

  parser = argparse.ArgumentParser()
  
  source_options = parser.add_mutually_exclusive_group(required=True)
  source_options.add_argument('-d', '--directory',
    help='the git repository path to the source code in the local machine.',
    type=Path,
    dest='git_path',
  )
  source_options.add_argument('-r', '--repo-url',
    help='the git repository url to the source code.',
    dest='git_url',
  )
  source_options.add_argument('-u', '--username',
    help='the username to check all repositores for.',
    metavar='git_username'
  )
  
  lookup_options = parser.add_mutually_exclusive_group()
  lookup_options.add_argument('--omit-repos',
    help='list of git repository names to ignore. Works with username option.',
    nargs='+'
  )
  lookup_options.add_argument('--use-repos',
    help='list of git repositories names to use, ignoring the rest. Works with username option.',
    nargs='+'
  )
  
  parser.add_argument('-b', '--branch',
    help='the git branch to run this script against inside a repository',
    default='main'
  )
  parser.add_argument('-p', '--provider',
    help='specifies the provider to query. Works alongside username option.',
    nargs='+',
    choices=['GitHub', 'GitLab', 'Codeberg'],
    default=['GitHub']
  )
  parser.add_argument('-v', '--verbose',
    help='Produce extended output',
    action='count',
    default=0
  )
  parser.add_argument('--version',
    action='version',
    version=f'%(prog)s {CURRENT_VERSION}'
  )

  return parser.parse_args()


# INITIALIZE LOGGER INSTANCE AND CUSTOM FORMATTER
# Custom format class to print using colors. Credit:
# https://alexandra-zaharia.github.io/posts/make-your-own-custom-color-formatter-with-python-logging/

logger = logging.getLogger(__name__)

class CustomFormatter(logging.Formatter):
  """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

  gray = '\x1b[38;5;240m'
  blue = '\x1b[38;5;39m'
  yellow = '\x1b[38;5;220m'
  orange = '\x1b[38;5;202m'
  red = '\x1b[38;5;160m'
  reset = '\x1b[0m'

  def __init__(self, fmt):
    super().__init__()
    self.fmt = fmt
    self.FORMATS = {
      logging.DEBUG: f'{self.gray}{self.fmt}{self.reset}',
      logging.INFO: f'{self.blue}{self.fmt}{self.reset}',
      logging.WARNING: f'{self.yellow}{self.fmt}{self.reset}',
      logging.ERROR: f'{self.orange}{self.fmt}{self.reset}',
      logging.CRITICAL: f'{self.red}{self.fmt}{self.reset}',
    }

  def format(self, record):
    log_fmt = self.FORMATS.get(record.levelno)
    formatter = logging.Formatter(log_fmt)
    return formatter.format(record)


if __name__ == '__main__':
  main()