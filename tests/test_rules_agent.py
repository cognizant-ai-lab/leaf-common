"""
Unit tests for RulesAgent
"""
import os
import tempfile
from unittest import TestCase

from leaf_common.rule_based.rules_agent import RulesAgent

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_PATH = os.path.join(ROOT_DIR, 'fixtures')


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
