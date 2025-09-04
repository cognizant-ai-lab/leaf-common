
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

from typing import Any
from typing import List
from typing import Tuple
from typing import Type

from leaf_common.config.resolver import Resolver


class ResolverUtil:
    """
    Helper class for creating instances of classes that are referenced by a string.
    """

    @staticmethod
    def create_instance(class_name: str, class_name_source: str, type_of_class: Type) -> Any:
        """
        Resolves the class_name to instantiate an instance of the class.
        Goes through some standard checking with standard exceptions thrown
        to make sure the class is set up the way we want it.

        :param class_name: The fully qualified class name to instantiate
        :param class_name_source: A string description of where we are getting the value of
                    class_name, so that exceptions can be more instructive.
        :param type_of_class: The type that the instance must be in order to pass muster.
        :return: An instance of the class referred to by class_name if everything is successful.
                Can return None if class_name is a None or empty string.
        """

        instance: Any = None
        class_reference: Type[Any] = ResolverUtil.create_class(class_name, class_name_source, type_of_class)

        if class_reference is None:
            return None

        # Instantiate the class
        try:
            instance = class_reference()
        except TypeError as exception:
            raise ValueError(f"Class '{class_name}' from {class_name_source} "
                             "must have a no-args constructor") from exception

        return instance

    @staticmethod
    def create_class(class_name: str, class_name_source: str, type_of_class: Type) -> Type:
        """
        Resolves a fully qualified class name string into an actual Python class object.

        This method expects the input string to follow the format:
        '<package>.<module>.<ClassName>' and uses a Resolver to dynamically
        locate and return the class object.

        :param class_name: The fully qualified name of the class to resolve.
        :param class_name_source: A description of the source of the class_name string,
                used for clearer error messages.
        :param type_of_class: Base type or interface the class must inherit from.
        :return: The resolved class object. Can return None if class_name is a None or empty string.
        """

        if class_name is None or len(class_name) == 0:
            return None

        # Split the single string into package, module, and class name
        class_split: List[str] = class_name.split(".")
        if len(class_split) <= 2:
            raise ValueError(f"Value from {class_name_source} '{class_name}' "
                             "must be of the form <package_name>.<module_name>.<ClassName>")

        packages: List[str] = [".".join(class_split[:-2])]
        class_name: str = class_split[-1]
        resolver = Resolver(packages)

        # Resolve the class name
        class_reference: Type[Any] = None
        try:
            class_reference = resolver.resolve_class_in_module(class_name, module_name=class_split[-2])
        except AttributeError as exception:
            raise ValueError(f"Class '{class_name}' from {class_name_source} "
                             "not found in PYTHONPATH") from exception

        # Make sure it is the correct type
        if not issubclass(class_reference, type_of_class):
            raise ValueError(
                f"Class {class_name} in {class_name_source} must be a subclass of {type_of_class.__name__}"
            )

        return class_reference

    @staticmethod
    def create_type(fully_qualified_name: str,
                    raise_if_not_found: bool = True,
                    install_if_missing: str = None) -> Type[Any]:
        """
        :param fully_qualified_name: The fully qualified name of the class to create
        :param raise_if_not_found: Raise an exception if the class is not found when True.
        :param install_if_missing: The pip package to install if the class is not found
        :return: The class referenced (*not* an instance of the class).
                 Can return None if the class is not found and raise_if_not_found is False.
        """
        if not fully_qualified_name:
            return None

        name_split: List[str] = fully_qualified_name.split(".")
        module_name: str = ".".join(name_split[:-1])
        class_name: str = name_split[-1]

        resolver = Resolver()
        class_type: Type[Any] = resolver.resolve_class_in_module(class_name,
                                                                 module_name=module_name,
                                                                 raise_if_not_found=raise_if_not_found,
                                                                 install_if_missing=install_if_missing)
        return class_type

    @staticmethod
    def create_type_tuple(type_list: List[str]) -> Tuple[Type[Any], ...]:
        """
        Creates a tuple of class types for use in isinstance(obj, <tuple_of_types>)
        situations.

        :param type_list: A list of fully qualified names of the types to create
                          (not class instances) to the string name of the package to install
                          if the class is not found.
        :return: A tuple of the class types that could be resolved.
                Can return an empty tuple if nothing in the type_list could be resolved
        """

        if not type_list:
            return ()

        tuple_list: List[Type[Any]] = []
        for class_name in type_list:

            # Try to resolve the single type and append to list if we get it.
            one_type: Type[Any] = ResolverUtil.create_type(class_name,
                                                           raise_if_not_found=False,
                                                           install_if_missing=None)
            if one_type is not None:
                tuple_list.append(one_type)

        return tuple(tuple_list)
