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

    def test_get_representation_default(self):
        """
        Verify defaults to KerasNN
        """
        self.assertEqual(RepresentationType.KerasNN, RepresentationType.get_representation(self._experiment_params))

    def test_get_representation_explicit_keras_nn(self):
        """
        Verify explicitly specifying KerasNN works
        """
        self._experiment_params['LEAF'] = {}
        self._experiment_params['LEAF']['representation'] = 'KerasNN'
        self.assertEqual(RepresentationType.KerasNN, RepresentationType.get_representation(self._experiment_params))

    def test_get_representation_weights(self):
        """
        Verify NNWeights representation
        """
        self._experiment_params['LEAF'] = {}
        self._experiment_params['LEAF']['representation'] = 'NNWeights'
        self.assertEqual(RepresentationType.NNWeights, RepresentationType.get_representation(self._experiment_params))

    def test_get_representation_rules(self):
        """
        Verify Rules-based representation
        """
        self._experiment_params['LEAF'] = {}
        self._experiment_params['LEAF']['representation'] = 'RuleBased'
        self.assertEqual(RepresentationType.RuleBased, RepresentationType.get_representation(self._experiment_params))

    def test_get_representation_invalid(self):
        """
        Verify invalid representation case
        """
        self._experiment_params['LEAF'] = {}
        self._experiment_params['LEAF']['representation'] = 'not_valid'
        self.assertRaises(ValueError, RepresentationType.get_representation, self._experiment_params)

    def test_get_representation_null_params(self):
        """
        Verify default when None is passed
        """
        self.assertEqual(RepresentationType.KerasNN, RepresentationType.get_representation(None))
