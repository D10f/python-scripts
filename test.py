#! /usr/bin/env python3

import json

with open('file_extensions.json') as f:
  data = json.load(f)
  types = {}

  for item in data:
    if 'extensions' not in item:
      continue

    extensions = item['extensions']
    for ext in extensions:
      types.setdefault(ext, item['name'])

  print(types)