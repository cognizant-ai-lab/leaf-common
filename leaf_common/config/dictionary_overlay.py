
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
See class comment for details.
"""


class DictionaryOverlay():
    """
    Policy class assisting with deep dictionary updates.
    """

    def overlay(self, basis, overlay, allow_overlay_only_items=True):
        """
        :param basis: The basis dictionary to be overlayed.
                        Unmodified on exit.
        :param overlay: The overlay dictionary.
                        Unmodified on exit.
        :param allow_overlay_only_items:
                             True, if we allow some keys from "overlay"
                                   not to be present in "basis",
                             False otherwise. In this case, if such keys are found,
                             we raise ValueError exception.
        :return: A new dictionary whose keys are the union of all
                keys between the two dictionaries and whose values
                favor the contents of the overlay dictionary.
                In the case where values in both the basis and overlay
                are both dictionaries, this method recurses.
        """

        overlay_only_items = set()
        result = self._do_overlay(basis, overlay, overlay_only_items, '')
        # Now, let's check if we had items present in "overlay"
        # but not in "basis" dictionary.
        # If YES - always print out warning message;
        # and if we don't allow overlay-only items, raise an exception.
        if len(overlay_only_items) > 0 \
                and not allow_overlay_only_items:
            separator = ', '
            message = separator.join(overlay_only_items)
            raise ValueError(f"overlay items not present in basis: {message}")
        return result

    def _do_overlay(self, basis, overlay, overlay_only_items, items_prefix):
        """
        :param basis: The basis dictionary to be overlayed.
                        Unmodified on exit.
        :param overlay: The overlay dictionary.
                        Unmodified on exit.
        :param overlay_only_items: set of dictionary keys
                                found in "overlay" but not in "basis".
                                This could be modified on exit.
        :param items_prefix: for keys to be put in "overlay_only_items",
                             prefix them with "items_prefix" for better diagnostics.
        :return: A new dictionary whose keys are the union of all
                keys between the two dictionaries and whose values
                favor the contents of the overlay dictionary.
                In the case where values in both the basis and overlay
                are both dictionaries, this method recurses.
        """

        # Preliminary argument checking
        if basis is None and overlay is None:
            return None

        if basis is None:
            basis = {}

        if not isinstance(basis, dict):
            raise ValueError("basis is not a dictionary")

        if overlay is None:
            overlay = {}

        if not isinstance(overlay, dict):
            raise ValueError("overlay is not a dictionary")

        # Do not modify any incoming arguments
        result = {}
        result.update(basis)

        for key in overlay.keys():

            # Any key we do not have, we just copy over the value from overlay.
            if key not in basis:
                result[key] = overlay[key]
                overlay_only_items.add(items_prefix+key)
                continue

            basis_value = basis.get(key)
            overlay_value = overlay.get(key)

            if basis_value is not None \
                    and overlay_value is not None:
                # Adjust overlay value type here:
                # if "basis" contains say A = 3 and overlay contains A = '3',
                # we try to convert overlay string to numeric type
                # by parsing it. This takes care of situation
                # when overlay value comes from environment variable,
                # which is always a string.
                overlay_value = self._convert_overlay_value(basis_value, overlay_value)

            # By default, the result value for the key will be the overlay
            # value itself.
            result_value = overlay_value

            # ... except if both values are dictionaries.
            # In that case, recurse.
            if isinstance(basis_value, dict) and \
               isinstance(overlay_value, dict):
                result_value = self._do_overlay(basis_value,
                                                overlay_value,
                                                overlay_only_items,
                                                f"{items_prefix}{key}.")

            result[key] = result_value

        return result

    def _convert_overlay_value(self, basis_value, overlay_value):
        """
        Given basis value from configuration and overlay value
        we need to replace it with, convert overlay value if necessary.
        If overlay value is a string and target basis value
        is numeric/boolean, we expect the overlay string to represent
        the correct value and parse it accordingly.

        :param basis_value: basis configuration value
        :param overlay_value: value taken from configuration overlay
        :return: converted overlay value to override basis value
                 in configuration.
        """

        if isinstance(overlay_value, str):
            if isinstance(basis_value, bool):
                overlay_value = \
                    bool(overlay_value.strip().lower() == 'true')
            elif isinstance(basis_value, int):
                overlay_value = int(float(overlay_value))
            elif isinstance(basis_value, float):
                overlay_value = float(overlay_value)
        return overlay_value
