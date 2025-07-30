# coding=utf-8
# Copyright 2022 The Google Research Authors.
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
"""Tests for utils."""

import dataclasses

from absl.testing import absltest
from connectomics.common import utils
import numpy as np


class UtilsTest(absltest.TestCase):

  def test_batch(self):
    seq = list(range(1, 11))
    batched = list(utils.batch(seq, 3))
    self.assertEqual(batched, [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]])

  def test_npdataclassjsonmixin(self):

    @dataclasses.dataclass
    class Test(utils.NPDataClassJsonMixin):
      foo: int
      bar: float

    v = Test(np.int64(123), np.float32(4.56))
    self.assertEqual(v, v.from_json(v.to_json()))


if __name__ == '__main__':
  absltest.main()
