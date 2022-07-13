
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
See class comment for details.
"""

import importlib
import logging
import re


class Resolver():
    """
    Class that handles resolving a class name in a module
    where the module might be found in one of many packages.
    """

    def __init__(self, packages):
        """
        :param packages: The list of packages to search
        """

        self.packages = packages

    def resolve_class_in_module(self, class_name, module_name=None,
                                raise_if_not_found=True,
                                verbose=False):
        """
        :param class_name: The name of the class we are looking for.
        :param module_name: The name of the module the class should be in.
                        Can be None, in which case the module name is taken
                        as the underscores version of the class name.
        :param raise_if_not_found: When True an error will be raised that
                        the class could not be resolved.
        :param verbose: Controls how chatty the process is. Default False.
        :return: a reference to the Python class, if the class could be resolved
                 None otherwise.
        """

        # See if we need to manufacture a module name from the class name
        use_module_name = module_name
        if use_module_name is None:
            use_module_name = self.module_name_from_class_name(class_name)

        logger = logging.getLogger(self.__class__.__name__)
        messages = []
        found_module = None
        if verbose:
            logger.info("Attempting to resolve module %s", use_module_name)
        for package in self.packages:
            fully_qualified_module = f"{package}.{use_module_name}"
            found_module = self.try_to_import_module(fully_qualified_module,
                                                     messages)
            if found_module is not None:
                break

        if found_module is None:
            message = f"Could not find code for {use_module_name}"
            messages.append(message)
            for message in messages:
                # Always print a message when we couldn't find something
                logger.info(message)
            if raise_if_not_found:
                raise ValueError(str(messages))
        elif verbose:
            logger.info("Found module %s", use_module_name)

        my_class = getattr(found_module, class_name)
        return my_class

    def try_to_import_module(self, module, messages):
        """
        Makes a single attempt to load a module
        :param module: The name of the module to load
        :param messages: a list of messages where logs of failed attempts can go
        :return: The python module if found. None if not found.
        """

        found_module = None
        message = None

        try:
            found_module = importlib.import_module(module)
        except SyntaxError as exception:
            message = \
                f"Module {module}: Couldn't load due to SyntaxError: {str(exception)}"
        except ImportError as exception:
            message = \
                f"Module {module}: Couldn't load due to ImportError: {str(exception)}"
            message += "...\n"
            message += "This might be OK if this is *not* an ImportError "
            message += "in the file itself and the code can be found in "
            message += "another directory"

        except Exception as exception:      # pylint: disable=broad-except
            message = f"Module {module}: Couldn't load due to Exception: {str(exception)}"

        if message is not None:
            messages.append(message)

        return found_module

    def module_name_from_class_name(self, class_name):
        """
        :param class_name: The class name whose module name we are looking for
        :return: the snake-case module name
        """

        # See https://stackoverflow.com/questions/1175208/
        #       elegant-python-function-to-convert-camelcase-to_snake_case
        sub_expr = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
        module_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', sub_expr).lower()

        return module_name
