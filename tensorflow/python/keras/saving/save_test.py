# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
"""Tests for Keras model saving code."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import numpy as np

from tensorflow.python import keras
from tensorflow.python.feature_column import feature_column_v2
from tensorflow.python.framework import test_util
from tensorflow.python.keras import testing_utils
from tensorflow.python.keras.saving import model_config
from tensorflow.python.keras.saving import save
from tensorflow.python.platform import test

try:
  import h5py  # pylint:disable=g-import-not-at-top
except ImportError:
  h5py = None


class TestSaveModel(test.TestCase):

  def setUp(self):
    self.model = testing_utils.get_small_sequential_mlp(1, 2, 3)
    self.subclassed_model = testing_utils.get_small_subclass_mlp(1, 2)

  def assert_h5_format(self, path):
    if h5py is not None:
      self.assertTrue(h5py.is_hdf5(path),
                      'Model saved at path {} is not a valid hdf5 file.'
                      .format(path))

  @test_util.run_v2_only
  def test_save_format_defaults(self):
    path = os.path.join(self.get_temp_dir(), 'model_path')

    # The default is currently HDF5 no matter what the filepath is.
    save.save_model(self.model, path)
    self.assert_h5_format(path)

  @test_util.run_v2_only
  def test_save_hdf5(self):
    path = os.path.join(self.get_temp_dir(), 'model')
    save.save_model(self.model, path, save_format='h5')

    self.assert_h5_format(path)

  @test_util.run_v2_only
  def test_save_tf(self):
    path = os.path.join(self.get_temp_dir(), 'model')
    with self.assertRaisesRegexp(
        NotImplementedError,
        'Saving the model as SavedModel is still in experimental stages.'):
      save.save_model(self.model, path, save_format='tf')

  @test_util.run_in_graph_and_eager_modes
  def test_saving_with_dense_features(self):
    cols = [feature_column_v2.numeric_column('a')]
    input_layer = keras.layers.Input(shape=(1,), name='a')
    fc_layer = feature_column_v2.DenseFeatures(cols)({'a': input_layer})
    output = keras.layers.Dense(10)(fc_layer)

    model = keras.models.Model(input_layer, output)

    model.compile(
        loss=keras.losses.MSE,
        optimizer=keras.optimizers.RMSprop(lr=0.0001),
        metrics=[keras.metrics.categorical_accuracy])

    config = model.to_json()
    loaded_model = model_config.model_from_json(config)

    inputs = np.arange(10).reshape(10, 1)
    self.assertLen(loaded_model.predict({'a': inputs}), 10)


if __name__ == '__main__':
  test.main()
