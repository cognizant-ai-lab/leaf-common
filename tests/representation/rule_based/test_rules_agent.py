"""
Unit tests for RulesAgent
"""
import os
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

from leaf_common.representation.rule_based.rules_agent import RulesAgent
from leaf_common.representation.rule_based.rule_set_evaluator import RuleSetEvaluator
from leaf_common.representation.rule_based.rules_agent_file_persistence import RulesAgentFilePersistence
from leaf_common.representation.rule_based.rules_evaluation_constants \
    import RulesEvaluationConstants


class TestRulesAgent(TestCase):
    """
    Unit tests for RulesAgent
    """

    def __init__(self, *args, **kwargs):
        super(TestRulesAgent, self).__init__(*args, **kwargs)
        root_dir = os.path.dirname(os.path.abspath(__file__))
        self.fixtures_path = os.path.join(root_dir, '../..', 'fixtures')

    def test_serialize_roundtrip(self):
        """
        Verify simple roundtrip with serializer
        """
        agent = RulesAgent(states={'k1': 'value1'},
                           actions={'action1': 'action_value1'},
                           uid='test_rules_agent')

        with tempfile.NamedTemporaryFile('w') as saved_agent_file:
            persistence = RulesAgentFilePersistence()
            persistence.persist(agent, saved_agent_file.name)
            reloaded_agent = persistence.restore(saved_agent_file.name)

        self.assertIsNot(agent, reloaded_agent)

    def test_complex_agent_roundtrip(self):
        """
        Verify roundtrip with persisted agent "from the field" (gen 50 Flappy Bird)
        """
        rules_file = os.path.join(self.fixtures_path, 'saved_agent.rules')
        persistence = RulesAgentFilePersistence()
        agent = persistence.restore(rules_file)

        with tempfile.NamedTemporaryFile('w') as saved_agent_file:
            persistence = RulesAgentFilePersistence()
            persistence.persist(agent, saved_agent_file.name)
            reloaded_agent = persistence.restore(saved_agent_file.name)

        self.assertIsNot(agent, reloaded_agent)

    @patch("leaf_common.representation.rule_based.rule_set_evaluator.RuleEvaluator.evaluate",
           return_value=Mock())
    def test_parse_rules_agree(self, evaluate_mock):
        """
        Verify correct parsing of rules
        """

        # Set it up so mock rules agree on action1
        agent, num_rules = self._create_rules_agent(
            rule1_action={RulesEvaluationConstants.ACTION_KEY: 'action1'},
            rule2_action={RulesEvaluationConstants.ACTION_KEY: 'action1'})

        self.assertEqual(num_rules, len(agent.rules))

        evaluate_mock.side_effect = [
            {RulesEvaluationConstants.ACTION_KEY: 'action1'},
            {RulesEvaluationConstants.ACTION_KEY: 'action1'}
        ]

        evaluator = RuleSetEvaluator()
        result = evaluator.parse_rules(agent)

        self.assertEqual(num_rules, len(result))
        self.assertTrue('action1' in result)
        self.assertTrue('action2' in result)
        self.assertEqual(num_rules, result['action1'])
        self.assertEqual(0, result['action2'])

    @patch("leaf_common.representation.rule_based.rule_set_evaluator.RuleEvaluator.evaluate",
           return_value=Mock())
    def test_parse_rules_disagree(self, evaluate_mock):
        """
        Verify correct parsing of rules
        """

        # Set it up so mock rules vote differently -- 1 for action1, 1 for action2
        agent, num_rules = self._create_rules_agent(
            rule1_action={RulesEvaluationConstants.ACTION_KEY: 'action1'},
            rule2_action={RulesEvaluationConstants.ACTION_KEY: 'action2'})

        self.assertEqual(num_rules, len(agent.rules))

        evaluate_mock.side_effect = [
            {RulesEvaluationConstants.ACTION_KEY: 'action1'},
            {RulesEvaluationConstants.ACTION_KEY: 'action2'}
        ]

        evaluator = RuleSetEvaluator()
        result = evaluator.parse_rules(agent)

        print("test result = ", str(result))
        self.assertEqual(num_rules, len(result))
        self.assertTrue('action1' in result)
        self.assertTrue('action2' in result)
        self.assertEqual(1, result['action1'])
        self.assertEqual(1, result['action2'])

    @staticmethod
    def _create_rules_agent(rule1_action, rule2_action):
        mock_rule_1 = MagicMock()
        mock_rule_2 = MagicMock()
        mock_rule_1.conditions = [MagicMock()]
        mock_rule_2.conditions = [MagicMock()]
        mock_rule_1.parse.return_value = rule1_action
        mock_rule_2.parse.return_value = rule2_action
        agent = RulesAgent(states={'k1': 'value1', 'k2': 'value2'},
                           actions={
                                'action1': 'action_value1',
                                'action2': 'action_value2'
                           })
        agent.rules.append(mock_rule_1)
        agent.rules.append(mock_rule_2)
        return agent, len(agent.rules)
