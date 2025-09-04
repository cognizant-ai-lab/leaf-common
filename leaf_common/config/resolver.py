
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
from typing import Type

from importlib import import_module
from logging import getLogger
from logging import Logger
from re import sub


class Resolver():
    """
    Class that handles resolving a class name in a module
    where the module might be found in one of many packages.
    """

    def __init__(self, packages: List[str] = None):
        """
        :param packages: The list of packages to search
        """

        self.packages: List[str] = packages

    # pylint: disable=too-many-positional-arguments,too-many-arguments
    def resolve_class_in_module(self, class_name: str, module_name: str = None,     # noqa: C901
                                raise_if_not_found: bool = True,
                                verbose: bool = False,
                                install_if_missing: str = None) -> Type[Any]:
        """
        :param class_name: The name of the class we are looking for.
        :param module_name: The name of the module the class should be in.
                        Can be None, in which case the module name is taken
                        as the underscores version of the class name.
        :param raise_if_not_found: When True an error will be raised that
                        the class could not be resolved.
        :param verbose: Controls how chatty the process is. Default False.
        :param install_if_missing: Optional name of a package to install if the module is missing.
        :return: a reference to the Python class, if the class could be resolved
                 None otherwise.
        """

        # See if we need to manufacture a module name from the class name
        use_module_name: str = module_name
        if use_module_name is None:
            use_module_name = self.module_name_from_class_name(class_name)

        logger: Logger = getLogger(self.__class__.__name__)
        messages: List[str] = []
        found_module: bool = None
        if verbose:
            logger.info("Attempting to resolve module %s", use_module_name)

        if self.packages is not None:
            for package in self.packages:
                fully_qualified_module: str = f"{package}.{use_module_name}"
                found_module: Any = self.try_to_import_module(fully_qualified_module,
                                                              messages, install_if_missing)
                if found_module is not None:
                    break
        else:
            found_module: Any = self.try_to_import_module(use_module_name, messages,
                                                          install_if_missing)

        if found_module is None:
            message: str = f"Could not find code for {use_module_name}"
            messages.append(message)
            for message in messages:
                # Always print a message when we couldn't find something
                logger.info(message)
            if raise_if_not_found:
                raise ValueError(str(messages))
        elif verbose:
            logger.info("Found module %s", use_module_name)

        # The None case here should only fall through if raise_not_found is False.
        my_class: Type[Any] = None
        if found_module is not None:
            my_class = getattr(found_module, class_name)

        return my_class

    def try_to_import_module(self, module: str, messages: List[str],
                             install_if_missing: str = None) -> Any:
        """
        Makes a single attempt to load a module

        :param module: The name of the module to load
        :param messages: a list of messages where logs of failed attempts can go
        :param install_if_missing: Optional name of a package to install if the module is missing.
        :return: The python module if found. None if not found.
        """

        # importlib source and docs gives no clue as to proper typing for modules. <shrug>
        found_module: Any = None
        message: str = None

        try:
            found_module = import_module(module)
        except SyntaxError as exception:
            message = \
                f"Module {module}: Couldn't load due to SyntaxError: {str(exception)}"
        except ImportError as exception:
            message = \
                f"Module {module}: Couldn't load due to ImportError: {str(exception)}"
            message += "...\n"
            if not install_if_missing:
                message += "This might be OK if this is *not* an ImportError "
                message += "in the file itself and the code can be found in "
                message += "another directory"
            else:
                message += f"Try pip installing the package {install_if_missing} to get past this error."

        except Exception as exception:      # pylint: disable=broad-except
            message = f"Module {module}: Couldn't load due to Exception: {str(exception)}"

        if message is not None:
            messages.append(message)

        return found_module

    def module_name_from_class_name(self, class_name: str) -> str:
        """
        :param class_name: The class name whose module name we are looking for
        :return: the snake-case module name
        """

        # See https://stackoverflow.com/questions/1175208/
        #       elegant-python-function-to-convert-camelcase-to_snake_case
        sub_expr: str = sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
        module_name: str = sub('([a-z0-9])([A-Z])', r'\1_\2', sub_expr).lower()

        return module_name
