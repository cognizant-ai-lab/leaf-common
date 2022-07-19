
# Copyright (C) 2019-2021 Cognizant Digital Business, Evolutionary AI.
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
Utilities for states (features)
"""

from leaf_common.representation.rule_based.data.rules_constants import RulesConstants


class States:
    """
    A class that encapsulates some utilities surrounding the parsing of
    states (features/columns).
    """

    @staticmethod
    def is_categorical(feature_name: str) -> bool:
        """
        Check if condition is categorical

        DEF: Hormoz: I need some therapy.  Some docs as to the conventions of the
                    formatting of categorical features is in order here.

        :param feature_name: if you are expecting me to tell you what this is you need therapy
        :return: Boolean
        """
        return RulesConstants.CATEGORY_EXPLAINABLE_MARKER in feature_name

    @staticmethod
    def extract_categorical_feature_name(feature_name: str) -> str:
        """
        Extract the name of the categorical condition from the name string
        :param feature_name: if you are expecting me to tell you what this is you need therapy
        :return: Str
        """
        return feature_name.split(RulesConstants.CATEGORY_EXPLAINABLE_MARKER)[0]

    @staticmethod
    def extract_categorical_feature_category(feature_name: str) -> str:
        """
        Extract the category name from the name string
        :param feature_name: if you are expecting me to tell you what this is you need drugs
        :return: Str
        """
        return feature_name.split(RulesConstants.CATEGORY_EXPLAINABLE_MARKER)[1]
