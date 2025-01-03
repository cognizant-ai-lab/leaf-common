
# Copyright (C) 2019-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# leaf-common SDK Software in commercial settings.
#
# END COPYRIGHT
"""
See class comment for details
"""

from typing import Dict, List, Any

from leaf_common.representation.rule_based.data.rules_constants import RulesConstants


class RuleSetConfigHelper:
    """
    Rule-set config helper class.
    """

    @staticmethod
    def get_states(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract states from Esp configuration
        :param config: Esp config
        :return: states
        """
        states = RuleSetConfigHelper.read_config_shape_var(config['network']['inputs'])
        return states

    @staticmethod
    def get_actions(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract actions from Esp configuration
        :param config: Esp config
        :return: actions
        """
        actions = RuleSetConfigHelper.read_config_shape_var(config['network']['outputs'])
        return actions

    @staticmethod
    def read_config_shape_var(config_vars: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        This method handles the following two examples of defining network parameters into an enumerated list of them:
        FIRST CASE EXAMPLE:
        "network": {
            "inputs": [
                {
                    "name": "context",
                    "size": 21,
                    "values": [
                        "float"
                    ]
                }
            ],

        SECOND CASE EXAMPLE:
        "network": {
            "inputs": [
                {
                    "name": "param1",
                    "size": 1,
                    "values": [
                        "float"
                    ]
                },
                {
                    "name": "param2",
                    "size": 1,
                    "values": [
                        "float"
                    ]
                }, ... etc.

        THIRD CASE EXAMPLE: (including the return values format)
            INPUT/STATES:
                [{'name': 'admission_source_id', 'size': 6, 'values': ['Court/Law Enforcement',
                                                                        'Emergency Room',
                                                                        'Medical Healthcare Professional Referral',
                                                                        'Not Available', 'Pregnancy',
                                                                        'Transfer from another Medical Facility']},
                                                                         ... etc.
                {'0': 'admission_source_id_is_category_Court/Law Enforcement',
                '1': 'admission_source_id_is_category_Emergency Room',
                '2': 'admission_source_id_is_category_Medical Healthcare Professional Referral',
                '3': 'admission_source_id_is_category_Not Availaible',
                '4': 'admission_source_id_is_category_Pregnancy',
                '5': 'admission_source_id_is_category_Transfer from another Medical Facility',
                ... etc.

            OUTPUT/ACTIONS:
                [{'name': 'acarbose', 'size': 2, 'activation': 'softmax', 'use_bias': True, 'values': ['No', 'Yes']},
                ... etc.
                {'0': 'acarbose_is_category_No',
                '1': 'acarbose_is_category_Yes',
                ... etc.


        :param config_vars: A dictionary definition of input or output parameters of a domain
        :return: A dictionary enumerating the parameter definition
        """

        var_index = 0
        var = {}
        for var_item in config_vars:
            the_size = int(var_item['size'])
            if the_size > 1:
                if 'values' in var_item and len(var_item['values']) == the_size:
                    for i in range(the_size):
                        var[str(var_index)] = \
                            var_item['name'] + RulesConstants.CATEGORY_EXPLAINABLE_MARKER + var_item['values'][i]
                        var_index += 1
                else:
                    for i in range(the_size):
                        var[str(var_index)] = \
                            var_item['name'] + RulesConstants.CATEGORY_EXPLAINABLE_MARKER + 'io_' + str(i)
                        var_index += 1
            else:
                var[str(var_index)] = var_item['name']
                var_index += 1
        return var
