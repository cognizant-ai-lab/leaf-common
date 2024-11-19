
from typing import Any
from typing import Dict
from typing import List


class FieldInfoUtil:
    """
    Utility methods to be used on the "info" dictionary created by the
    DataFrameProfiler.
    """

    @staticmethod
    def is_categorical(field_name: str, field_infos: Dict[str, Any]):
        """
        Returns true if the field is categorical, false if it's numerical

        :param field_name: a context, action or outcome field name
        :param field_infos: a dictionary containing the fields "info" description
                        from a data profile or a data tag node.
        :return: true if the field is categorical, false otherwise
        """
        is_cat = False

        if field_infos is None:
            # No dictionary
            return is_cat

        if field_name is None:
            # No field name
            return is_cat

        # Get the field info dictionary
        field_info = field_infos.get(field_name)
        if field_info is None:
            # No field in dictionary
            return is_cat

        # Here we offer some compatibility with some fields that might be found
        # with hacky overlays onto this structure of UI data.  While not
        # completely appropriate at this level of code, the only thing used
        # here are independent definitions of string keys.
        valued = field_info.get("valued", None)

        data_type = field_info.get("data_type", None)

        if valued is not None:
            # "valued" is a field set by the user on the data tag node
            # Take that as gospel if it's categorical.
            if valued.lower() == "categorical":
                is_cat = True
        elif data_type.lower() == "string":
            # "data_type" is a field set by the DataFrameProfiler.
            # Anything that is a string is automatically categorical
            is_cat = True

        return is_cat

    @staticmethod
    def get_unique_values(field_name: str, field_infos: Dict[str, Any]) -> List[Any]:
        """
        Returns the list of categorical values a categorical field can take

        :param: field_name: the name of the field to look for
        :param field_infos: a dictionary containing the fields "info" description
                        from a data profile or a data tag node.
        :return: the list of values this field can take
        """
        if not FieldInfoUtil.is_categorical(field_name, field_infos):
            return None

        field_info = field_infos.get(field_name)
        return field_info.get("discrete_categorical_values")
