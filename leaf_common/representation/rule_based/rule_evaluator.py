"""
Base class for rule representation
"""

from typing import Dict
from typing import List

from leaf_common.evaluation.component_evaluator import ComponentEvaluator
from leaf_common.representation.rule_based.rule import Rule
from leaf_common.representation.rule_based.condition_evaluator import ConditionEvaluator
from leaf_common.representation.rule_based.rules_evaluation_constants \
    import RulesEvaluationConstants


class RuleEvaluator(ComponentEvaluator):
    """
    ComponentEvaluator implementation for the Rule class

    Upon exit from evaluate() the following fields in Rule might be modified:
        * times_applied
    """

    def __init__(self, states: Dict[str, str]):
        # The ConditionEvaluator itself is stateless, so it's OK to just create
        # one here as an optimization
        self.condition_evaluator = ConditionEvaluator(states)

    def evaluate(self, component: Rule,
                 evaluation_data: Dict[str, object] = None) -> List[object]:
        """
        :return: A list containing an action indicator, and a lookback value or 0 for no lookback
        """

        rule = component

        for condition in rule.conditions:
            condition_result = self.condition_evaluator.evaluate(condition, evaluation_data)
            if not condition_result:
                return [RulesEvaluationConstants.NO_ACTION, 0]

        observation_history = evaluation_data[RulesEvaluationConstants.OBSERVATION_HISTORY_KEY]
        nb_states = len(observation_history) - 1

        # If the lookback is greater than the number of states we have, we can't evaluate the condition so
        # default to RulesEvaluationConstants.NO_ACTION
        if nb_states < rule.action_lookback:
            return [RulesEvaluationConstants.NO_ACTION, 0]

        rule.times_applied += 1
        if rule.action_lookback == 0:
            return [rule.action, 0]

        return [RulesEvaluationConstants.LOOK_BACK, rule.action_lookback]
