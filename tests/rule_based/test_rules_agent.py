"""
Unit tests for RulesAgent
"""
import os
import tempfile
from unittest import TestCase
from unittest.mock import patch, MagicMock

from leaf_common.rule_based.rule import THE_ACTION
from leaf_common.rule_based.rules_agent import RulesAgent

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(ROOT_DIR, '..', 'fixtures')


class TestRulesAgent(TestCase):
    """
    Unit tests for RulesAgent
    """
    def test_serialize_roundtrip(self):
        """
        Verify simple roundtrip with serializer
        """
        agent = RulesAgent(states={'k1': 'value1'}, actions={'action1': 'action_value1'}, uid='test_rules_agent',
                           initial_state={'state1': 'value1'})

        with tempfile.NamedTemporaryFile('w') as saved_agent_file:
            agent.save(saved_agent_file.name)

            reloaded_agent = RulesAgent.load(saved_agent_file.name)

        self.assertIsNot(agent, reloaded_agent)
        self.assertEqual(agent, reloaded_agent)

    def test_complex_agent_roundtrip(self):
        """
        Verify roundtrip with persisted agent "from the field" (gen 50 Flappy Bird)
        """
        rules_file = os.path.join(FIXTURES_PATH, 'saved_agent.rules')
        agent = RulesAgent.load(rules_file)

        with tempfile.NamedTemporaryFile('w') as saved_agent_file:
            agent.save(saved_agent_file.name)

            reloaded_agent = RulesAgent.load(saved_agent_file.name)

        self.assertIsNot(agent, reloaded_agent)
        self.assertEqual(agent, reloaded_agent)

    def test_parse_rules_agree(self):
        """
        Verify correct parsing of rules
        """

        # Set it up so mock rules agree on action1
        agent, num_rules = self._create_rules_agent(rule1_action={THE_ACTION: 'action1'},
                                                    rule2_action={THE_ACTION: 'action1'})

        self.assertEqual(num_rules, len(agent.rules))

        result = agent.parse_rules()
        self.assertEqual(num_rules, len(result))
        self.assertTrue('action1' in result)
        self.assertTrue('action2' in result)
        self.assertEqual(num_rules, result['action1'])
        self.assertEqual(0, result['action2'])

    def test_parse_rules_disagree(self):
        """
        Verify correct parsing of rules
        """

        # Set it up so mock rules vote differently -- 1 for action1, 1 for action2
        agent, num_rules = self._create_rules_agent(rule1_action={THE_ACTION: 'action1'},
                                                    rule2_action={THE_ACTION: 'action2'})

        self.assertEqual(num_rules, len(agent.rules))

        result = agent.parse_rules()
        self.assertEqual(num_rules, len(result))
        self.assertTrue('action1' in result)
        self.assertTrue('action2' in result)
        self.assertEqual(1, result['action1'])
        self.assertEqual(1, result['action2'])

    @staticmethod
    def _create_rules_agent(rule1_action, rule2_action):
        with patch('leaf_common.rule_based.rules_agent.Rule', autospec=True) as mock_rule, \
                patch('leaf_common.rule_based.rules_agent.random.randint', autospec=True) as mock_randint:
            mock_rule_1 = MagicMock()
            mock_rule_2 = MagicMock()
            mock_rule_1.conditions = [MagicMock()]
            mock_rule_2.conditions = [MagicMock()]
            mock_rule_1.parse.return_value = rule1_action
            mock_rule_2.parse.return_value = rule2_action
            mock_rule.side_effect = [mock_rule_1, mock_rule_2]
            num_rules = 2
            mock_randint.return_value = num_rules
            agent = RulesAgent(states={'k1': 'value1', 'k2': 'value2'},
                               actions={'action1': 'action_value1', 'action2': 'action_value2'},
                               initial_state={'state1': 'value1'})
            return agent, num_rules
