
# Copyright © 2019-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
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
See class comment for details.
"""

from os import path


class ReferenceHelper():
    """
    A class to help with breaking up full references to files
    into components used by the persistence system.

    XXX At some point this might be extended to include schemes and hosts
        for urls
    """

    @classmethod
    def get_components(cls, full_ref=None, folder=".",
                       base_name=None, file_extension=None):
        """
        :return: a triple of folder, basename and file extension to use
        """

        use_base_name = base_name
        use_folder = folder
        use_file_extension = file_extension

        if full_ref is not None:

            # Determine the folder from the full ref
            use_folder = path.dirname(full_ref)
            if len(use_folder) == 0:
                # If there is no folder, use what was passed in
                use_folder = folder

            # Determine the basename from the full ref
            use_base_name = path.basename(full_ref)
            (use_base_name, use_file_extension) = path.splitext(use_base_name)
            if len(use_file_extension) == 0:
                # If there is no file extension, use what was passed in
                use_file_extension = file_extension

        return use_folder, use_base_name, use_file_extension
