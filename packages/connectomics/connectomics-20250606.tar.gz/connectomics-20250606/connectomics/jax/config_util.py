# coding=utf-8
# Copyright 2024 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Helper tools for config files.

While configs should remain simple and self-explanatory, it can also be very
useful to augment the configs with a bit of logic that helps organizing
complicated sweeps.

This module contains shared code that allows for powerful uncluttered configs.
"""

from typing import Any, Sequence

import ml_collections as mlc


def parse_arg(arg, lazy=False, **spec):
  """Makes ConfigDict's get_config single-string argument more usable.

  Example use in the config file:

    import big_vision.configs.common as bvcc
    def get_config(arg):
      arg = bvcc.parse_arg(arg,
          res=(224, int),
          runlocal=False,
          schedule='short',
      )

      # ...

      config.shuffle_buffer = 250_000 if not arg.runlocal else 50

  Ways that values can be passed when launching:

    --config amazing.py:runlocal,schedule=long,res=128
    --config amazing.py:res=128
    --config amazing.py:runlocal  # A boolean needs no value for "true".
    --config amazing.py:runlocal=False  # Explicit false boolean.
    --config amazing.py:128  # The first spec entry may be passed unnamed alone.

  Uses strict bool conversion (converting 'True', 'true' to True, and 'False',
    'false', '' to False).

  Args:
    arg: the string argument that's passed to get_config.
    lazy: allow lazy parsing of arguments, which are not in spec. For these,
      the type is auto-extracted in dependence of most complex possible type.
    **spec: the name and default values of the expected options.
      If the value is a tuple, the value's first element is the default value,
      and the second element is a function called to convert the string.
      Otherwise the type is automatically extracted from the default value.

  Returns:
    ConfigDict object with extracted type-converted values.
  """
  # Normalize arg and spec layout.
  arg = arg or ''  # Normalize None to empty string
  spec = {k: (v if isinstance(v, tuple) else (v, _get_type(v)))
          for k, v in spec.items()}

  result = mlc.ConfigDict(type_safe=False)  # For convenient dot-access only.

  # Expand convenience-cases for a single parameter without = sign.
  if arg and ',' not in arg and '=' not in arg:
    # (think :runlocal) If it's the name of sth in the spec (or there is no
    # spec), it's that in bool.
    if arg in spec or not spec:
      arg = f'{arg}=True'
    # Otherwise, it is the value for the first entry in the spec.
    else:
      arg = f'{list(spec.keys())[0]}={arg}'
      # Yes, we rely on Py3.7 insertion order!

  # Now, expand the `arg` string into a dict of keys and values:
  raw_kv = {raw_arg.split('=')[0]:
                raw_arg.split('=', 1)[-1] if '=' in raw_arg else 'True'
            for raw_arg in arg.split(',') if raw_arg}

  # And go through the spec, using provided or default value for each:
  for name, (default, type_fn) in spec.items():
    val = raw_kv.pop(name, None)
    result[name] = type_fn(val) if val is not None else default

  if raw_kv:
    if lazy:  # Process args which are not in spec.
      for k, v in raw_kv.items():
        result[k] = _autotype(v)
    else:
      raise ValueError(f'Unhandled config args remain: {raw_kv}')

  return result


def _get_type(v):
  """Returns type of v and for boolean returns a strict bool function."""
  if isinstance(v, bool):
    def strict_bool(x):
      assert x.lower() in {'true', 'false', ''}
      return x.lower() == 'true'
    return strict_bool
  return type(v)


def _autotype(x):
  """Auto-converts string to bool/int/float if possible."""
  assert isinstance(x, str)
  if x.lower() in {'true', 'false'}:
    return x.lower() == 'true'  # Returns as bool.
  try:
    return int(x)  # Returns as int.
  except ValueError:
    try:
      return float(x)  # Returns as float.
    except ValueError:
      return x  # Returns as str.


def sequence_to_string(x: Sequence[Any], separator: str = ',') -> str:
  """Converts sequence of str/bool/int/float to a concatenated string."""
  return separator.join([str(i) for i in x])


def string_to_sequence(x: str, separator: str = ',') -> Sequence[Any]:
  """Converts string to sequence of str/bool/int/float with auto-conversion."""
  return [_autotype(i) for i in x.split(separator)]
