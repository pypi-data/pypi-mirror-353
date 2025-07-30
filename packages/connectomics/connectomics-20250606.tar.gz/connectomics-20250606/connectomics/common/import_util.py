# coding=utf-8
# Copyright 2024 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Functions for dynamically importing symbols from modules."""

import importlib
from absl import logging


def import_symbol(
    specifier: str, default_packages: str = 'connectomics.jax.models'
):
  """Imports a symbol from a python module.

  The calling module must have the target module for the import as dependency.

  Args:
    specifier: full path specifier in format
      [<packages>.]<module_name>.<model_class>, if packages is missing
      ``default_packages`` is used. Alternatively, the specifier can be just a
      class name within a module specified by default_packages.
    default_packages: chain of packages before module in format
      <top_pack>.<sub_pack>.<subsub_pack> etc.

  Returns:
    symbol: object from module
  """

  try:
    module_path, symbol_name = specifier.rsplit('.', 1)
  except ValueError as _:
    module_path = default_packages
    symbol_name = specifier

  try:
    logging.info(
        'Importing symbol %s from %s.%s',
        symbol_name,
        default_packages,
        module_path,
    )
    module = importlib.import_module(default_packages + '.' + module_path)
  except ImportError as e:
    logging.info(e)
    logging.info('Importing symbol %s from %s', symbol_name, module_path)
    module = importlib.import_module(module_path)

  symbol = getattr(module, symbol_name)
  return symbol
