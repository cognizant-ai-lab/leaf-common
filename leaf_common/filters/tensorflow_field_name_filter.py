
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
Copyright (C) 2021-2023 Cognizant Digital Business, Evolutionary AI.
All Rights Reserved.
Issued under the Academic Public License.

You can be released from the terms, and requirements of the Academic Public
License by purchasing a commercial license.
Purchase of a commercial license is mandatory for any use of the
unileaf-util SDK Software in commercial settings.

END COPYRIGHT
"""

from leaf_common.filters.inclusionary_replacement_string_filter import InclusionaryReplacementStringFilter
from leaf_common.filters.composite_string_filter import CompositeStringFilter
from leaf_common.filters.replacement_string_filter import ReplacementStringFilter
from leaf_common.filters.strip_whitespace_string_filter import StripWhitespaceStringFilter


class TensorFlowFieldNameFilter(CompositeStringFilter):
    """
    A StringFilter implementation whose filter() method filters input strings
    in such a way that they are suitable as TensorFlow column names as per
    https://stackoverflow.com/questions/51876460/getting-tensorflow-s-is-not-valid-scope-name-error-while-i-am-trying-to-creat

        _VALID_SCOPE_NAME_REGEX = re.compile("^[A-Za-z0-9_.\\-/>]*$")

        So in other words, scope names can contain letters (upper and lowercase),
        numbers, and _, ., backslash, -, /,>. (Notably, they can't include whitespace.)
    """

    def __init__(self):
        """
        Constructor which sets up a list of StringFilters to apply in order
        """
        filter_classes = [

            # Simply remove any initial or trailing whitespace
            StripWhitespaceStringFilter(),

            # Selected common substitutions. Sources:
            #   https://oinam.github.io/entities/
            ReplacementStringFilter(find="@", replace_with="commat"),
            ReplacementStringFilter(find="#", replace_with="num"),
            ReplacementStringFilter(find="$", replace_with="dollar"),
            ReplacementStringFilter(find="%", replace_with="percnt"),
            ReplacementStringFilter(find="^", replace_with="Hat"),
            ReplacementStringFilter(find="&", replace_with="amp"),
            ReplacementStringFilter(find="*", replace_with="ast"),
            ReplacementStringFilter(find="(", replace_with="lpar"),
            ReplacementStringFilter(find=")", replace_with="rpar"),
            ReplacementStringFilter(find="+", replace_with="plus"),
            ReplacementStringFilter(find="=", replace_with="equals"),
            ReplacementStringFilter(find="{", replace_with="lcub"),
            ReplacementStringFilter(find="}", replace_with="rcub"),
            ReplacementStringFilter(find="[", replace_with="lsqb"),
            ReplacementStringFilter(find="]", replace_with="rsqb"),
            ReplacementStringFilter(find="<", replace_with="lt"),
            ReplacementStringFilter(find="|", replace_with="verbar"),
            ReplacementStringFilter(find=":", replace_with="colon"),
            ReplacementStringFilter(find=";", replace_with="semi"),
            ReplacementStringFilter(find="?", replace_with="quest"),
            ReplacementStringFilter(find="\"", replace_with="quot"),
            ReplacementStringFilter(find="'", replace_with="apos"),
            ReplacementStringFilter(find="`", replace_with="grave"),

            # No standard available, but we need to replace
            ReplacementStringFilter(find=" ", replace_with="_"),
            ReplacementStringFilter(find="!", replace_with="not"),
            ReplacementStringFilter(find="~", replace_with="tilde"),

            # Valid for TF, but these are exceptions
            #   * Forward slash '/' is actually a scoping delimiter in TF land, so usage
            #       of it in field names is still discouraged. See
            #       https://stackoverflow.com/questions/49237889/
            #           what-characters-are-allowed-in-tensorflow-variable-names/49238452#49238452
            #   * We are electing to replace greater than '>' so that it is symmetrical
            #       with the non-use of less than '<'
            ReplacementStringFilter(find=">", replace_with="gt"),
            ReplacementStringFilter(find="/", replace_with="sol"),

            # Keep valid chars and replace all others that have still survived with a hyphen.
            # Note that this list is still a subset of the TensorFlow regex. See exceptions above
            #   _VALID_SCOPE_NAME_REGEX = re.compile("^[A-Za-z0-9_.\\-/>]*$")
            InclusionaryReplacementStringFilter(
                    valid_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.\\-",
                    replace_invalid_with="-")
        ]
        super().__init__(filter_classes)
