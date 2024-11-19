from typing import Any
from typing import Dict
from typing import List
from typing import Set

from copy import deepcopy


class DataProfileFieldIntegration:
    """
    Utility class that handles the integration of multiple DataProfiler
    descriptions of a single field.
    """

    @staticmethod
    def integrate_all_fields(list_of_field_dicts: List[Dict[str, Dict[str, Any]]]) \
            -> Dict[str, Dict[str, Any]]:
        """
        Integrates multiple fields dictionaries each containing multiple field infos.
        :param list_of_field_dicts: A list of field dictionaries to integrate.
                The first in the list holds a special place in that it is the
                basis for the complete list of fields to be used in integrating
                other field dictionaries.
                The last in the list also holds a special place as it is assumed
                to contain any user preferences that should be kept intact.
        :return: A single field dictionary that integrates all fields between
                anything listed in list_of_field_dicts as per
                integrate_field_infos() below.
        """
        if list_of_field_dicts is None or \
                len(list_of_field_dicts) == 0:
            # No basis
            return None

        first_fields = list_of_field_dicts[0]
        if len(list_of_field_dicts) == 1:
            # Only one fields dict, so no integration to do.
            return first_fields

        last_fields = list_of_field_dicts[-1]

        # Loop through each of the fields as delineated in the first
        # in the list, determining which to use.
        fields = {}
        for field_name in first_fields:
            last_field_info = last_fields.get(field_name)
            if last_field_info is None:
                # If for some reason the field name is not found in the
                # last_fields' data, then we cannot know its CAO-ness,
                # so do not include it.
                print(f"Profile field {field_name} is not in the original DataTag.\n"
                      "Skipping because we cannot know its desired CAO-ness.")
                continue

            # Set up a list of field infos for single-field integration.
            field_infos = []
            for one_field_dict in list_of_field_dicts:
                field_info = one_field_dict.get(field_name)
                if field_info is not None:
                    field_infos.append(field_info)

            field_info = DataProfileFieldIntegration.integrate_field_infos(field_infos, field_name)
            if field_info is not None:
                fields[field_name] = field_info
            else:
                print(f"Integration for field {field_name} calls for removal")

        return fields

    @staticmethod
    # pylint: disable=too-many-branches
    def integrate_field_infos(field_infos: List[Dict[str, Any]],
                              field_name: str = None) -> Dict[str, Any]:
        """
        Integrate any number of different data profile's information about a single
        field.  For the case of a CONTINUOUS field, make sure the range
        that is returned incorporates any value from any profile.
        For the case of a CATEGORICAL field, make sure the list of values
        is the union of each profile's discrete_categorical_values.

        :param field_infos: A list of data_profiling field_infos
                Note that the first entry in the list has a special
                place above the rest in that it is assumed to have
                the most recent data profile information, for instance
                by a chain of DataFrameTransformations..
        :return: A single combined field_info or None if the combined
                field_info is deemed inappropriate for inclusion.
        """
        if len(field_infos) == 0:
            return None

        # Use the first profile as the new basis, but do not modify the original.
        field_info = deepcopy(field_infos[0])

        # Find the first profile with a "valued" field, which indicates
        # the user has tagged it specifically
        for one_field_info in field_infos:

            valued = one_field_info.get("valued", None)
            data_type = one_field_info.get("data_type")

            if valued is not None:
                # Store the valued-ness in our output field_info
                # and take its lead as the data_type
                field_info["valued"] = valued
                break

        # Take the stats from the first profile as golden,
        # however some aspects of field might have been modified by the user.
        if valued == "CONTINUOUS":
            if data_type in ("FLOAT", "INT"):

                # Extend both the min and max of the range to
                # include all profiles.

                # Start out with the lead
                profile_range = field_info.get("range")

                # It is possible that either the data confabulation or the
                # user-specified values might have stretched the range values,
                # so resolve that here to encompass any value from either
                # profile for the field.
                for one_field_info in field_infos:
                    other_range = one_field_info.get("range")

                    # Handle some special cases
                    if other_range is None:
                        continue

                    if profile_range is None:
                        # If for some reason the first entry did not
                        # have a range, this will take the other as gospel.
                        profile_range = other_range

                    # Extend the profile range
                    min_index = 0
                    profile_range[min_index] = min(profile_range[min_index],
                                                   other_range[min_index])
                    max_index = 1
                    profile_range[max_index] = max(profile_range[max_index],
                                                   other_range[max_index])

                # Store the results in the output field_info
                field_info["range"] = profile_range

        elif valued == "CATEGORICAL":

            # Extend the set of categorical values to include
            # all values from all profiles.

            # Start with an empty set
            union_set = set()
            has_string = False
            for one_field_info in field_infos:

                # Take the union of the two lists as sets.
                profile_set = DataProfileFieldIntegration.get_categorical_values_set(one_field_info,
                                                                                     field_name)
                union_set = union_set.union(profile_set)

                if one_field_info.get("data_type") == "STRING":
                    has_string = True

            categories = list(union_set)
            field_info["discrete_categorical_values"] = categories
            if len(categories) < 2:
                # Do not allow inappropriate numbers of categories
                # This can happen when integrating 2 data profiles where one
                # is transformed and the other is not.
                field_info = None

            if has_string:
                # If any one profile for the field that was a string,
                # that is our sign that perhaps a type change happened
                # during category reduction.  Use the string.
                field_info["data_type"] = "STRING"

        # else: If valued is None, then we take the first field info as-is,
        #       as it's assumed to come from the most recent data profile.
        #       of any modified data.

        return field_info

    @staticmethod
    def get_categorical_values_set(field_info: Dict[str, Any], field_name: str = None) -> Set[Any]:
        """
        Get the discrete_categorical_values field of a column's profiling
        info as a set.  These can come as:
            * a histogram/dictionary, in which case we care only about keys
            * a list, in which case we care about all values of the list.
              ...Unless the list only has a single value which is a warning
              from the DataProfiler. This means the field will be ignored,
              and the sets contents will be empty
        :return: A set of values from the profiling field.
        """
        # It can be useful to have the field_name for debugging info
        # but when that info is on all the time, it's too much.
        # At least leave the plumbing intact in case we need it again.
        _ = field_name

        empty = []
        profile_values = field_info.get("discrete_categorical_values", empty)

        if isinstance(profile_values, dict):
            # Sometimes these are given as a dictionary histogram
            profile_values = profile_values.keys()

        if len(profile_values) == 1 and \
                isinstance(profile_values[0], str) and \
                profile_values[0].startswith("<Column contains "):

            # If the categorical values contained a string warning from the
            # DataProfiler, then we don't really have enough info to combine.
            # Return the empty set.
            return set()

        profile_values = set(profile_values)
        return profile_values
