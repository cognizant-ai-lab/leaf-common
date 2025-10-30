
# Copyright 2025 Cognizant Technology Solutions Corp, www.cognizant.com.
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
Utilities for states (features)
"""

from leaf_common.representation.rule_based.data.rules_constants import RulesConstants


class Features:
    """
    A class that encapsulates some utilities surrounding the parsing of
    features (columns).

    Since categorical conditions/features will be converted to one-hot encoded,
    they will be divided into some booleans (to the number of categories they
    have) and we name them by the following component conventions:

    A) The feature name    followed by
    B) RulesConstants.CATEGORY_EXPLAINABLE_MARKER   followed by
    C) the category name.

    As an example:
        {
            '0': 'admission_source_id_is_category_Court/Law Enforcement',
            '1': 'admission_source_id_is_category_Emergency Room',
            '2': 'admission_source_id_is_category_Medical Healthcare Professional Referral',
            '3': 'admission_source_id_is_category_Not Availaible',
            '4': 'admission_source_id_is_category_Pregnancy',
            '5': 'admission_source_id_is_category_Transfer from another Medical Facility',
            ... etc.
        }

    Therefore, the is_categorical() and the other functions here are presented
    to determine if a feature is a categorical feature, or to determine which
    category the feature belongs to.
    """

    @staticmethod
    def is_categorical(feature_name: str) -> bool:
        """
        Check if condition is categorical

        :param feature_name: Value string per the example in the class comments.
        :return: Boolean
        """
        return RulesConstants.CATEGORY_EXPLAINABLE_MARKER in feature_name

    @staticmethod
    def extract_categorical_feature_name(feature_name: str) -> str:
        """
        Extract the name of the categorical condition from the name string
        :param feature_name: Value string per the example in the class comments.
        :return: Str
        """
        return feature_name.split(RulesConstants.CATEGORY_EXPLAINABLE_MARKER)[0]

    @staticmethod
    def extract_categorical_feature_category(feature_name: str) -> str:
        """
        Extract the category name from the name string
        :param feature_name: Value string per the example in the class comments.
        :return: Str
        """
        return feature_name.split(RulesConstants.CATEGORY_EXPLAINABLE_MARKER)[1]
