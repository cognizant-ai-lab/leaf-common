
# Copyright © 2019-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
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
#
# END COPYRIGHT
"""
Tests for `RepresentationType` enum
"""

from unittest import TestCase

from leaf_common.candidates.representation_types import RepresentationType

EXPERIMENT_PARAMS = {}


class TestRepresentationType(TestCase):
    """
    Tests for `RepresentationType` enum
    """
    def setUp(self):
        self._experiment_params = EXPERIMENT_PARAMS

    def get_representation(self, experiment_params):
        """
        Given a set of experiment_params, inspects those params to determine the model representation fornmat
        :param experiment_params: A set of experiment parameters in JSON format.
        :return: The element of this enum corresponding to the inferred representation type.
        """
        leaf_representation = RepresentationType.KerasNN
        leaf_params = experiment_params.get("LEAF", None) if experiment_params else None
        if leaf_params:
            # Default to KerasNN representation if not otherwise specified.
            representation_type_as_string = leaf_params.get("representation", RepresentationType.KerasNN.value)
            try:
                leaf_representation = RepresentationType[representation_type_as_string]
            except KeyError:
                # pylint: disable=raise-missing-from
                raise ValueError(f'Invalid representation type: "{representation_type_as_string}"')
        return leaf_representation

    def test_get_representation_default(self):
        """
        Verify defaults to KerasNN
        """
        self.assertEqual(RepresentationType.KerasNN, self.get_representation(self._experiment_params))

    def test_get_representation_explicit_keras_nn(self):
        """
        Verify explicitly specifying KerasNN works
        """
        self._experiment_params['LEAF'] = {}
        self._experiment_params['LEAF']['representation'] = 'KerasNN'
        self.assertEqual(RepresentationType.KerasNN, self.get_representation(self._experiment_params))

    def test_get_representation_weights(self):
        """
        Verify NNWeights representation
        """
        self._experiment_params['LEAF'] = {}
        self._experiment_params['LEAF']['representation'] = 'NNWeights'
        self.assertEqual(RepresentationType.NNWeights, self.get_representation(self._experiment_params))

    def test_get_representation_rules(self):
        """
        Verify Rules-based representation
        """
        self._experiment_params['LEAF'] = {}
        self._experiment_params['LEAF']['representation'] = 'RuleBased'
        self.assertEqual(RepresentationType.RuleBased, self.get_representation(self._experiment_params))

    def test_get_representation_invalid(self):
        """
        Verify invalid representation case
        """
        self._experiment_params['LEAF'] = {}
        self._experiment_params['LEAF']['representation'] = 'not_valid'
        self.assertRaises(ValueError, self.get_representation, self._experiment_params)

    def test_get_representation_null_params(self):
        """
        Verify default when None is passed
        """
        self.assertEqual(RepresentationType.KerasNN, self.get_representation(None))
