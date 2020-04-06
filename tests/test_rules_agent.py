import tempfile
from unittest import TestCase

from leaf_common.rule_based.rules_agent import RulesAgent


class TestRulesAgent(TestCase):
    def test_serialize_roundtrip(self):
        agent = RulesAgent(states={'k1': 'value1'}, actions={'action1': 'action_value1'}, uid='test_rules_agent',
                           initial_state={'state1': 'value1'})

        with tempfile.NamedTemporaryFile('w') as saved_agent_file:
            agent.save(saved_agent_file.name)

            reloaded_agent = RulesAgent.load(saved_agent_file.name)

        self.assertIsNot(agent, reloaded_agent)
        self.assertEqual(agent, reloaded_agent)
