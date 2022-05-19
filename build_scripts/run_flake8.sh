#!/usr/bin/env bash

# set -euo pipefail

UP_TO_SNUFF_DIRS=`ls -1`
IGNORE="build_scripts"

dirs=$1
if [ "x${dirs}" == "x" ]
then
    dirs=${UP_TO_SNUFF_DIRS}
fi

retval=0
for dir in ${dirs}
do
    # At end of loop ignore_this will be set if we need to ignore
    ignore_this=""

    # If we actually have a single file, skip it
    if [[ -f ${dir} ]]
    then
        ignore_this=${dir}
    fi
        
    # See if it's a directory we specifically want to ignore
    for ignore_dir in ${IGNORE}
    do
        if [ "x${ignore_dir}" == $"x${dir}" ]
        then
            ignore_this=${dir}
        fi
    done

    # If we do not need to ignore...
    if [ "x" == "x${ignore_this}" ]
    then
        echo "Running flake8 on directory '${dir}':"
        find "${dir}" -iname "*.py" | \
            xargs flake8 -j 0
        current_retval=$?
        if [ ${current_retval} -ne 0 ]
        then
            retval=${current_retval}
        fi
    fi
done

echo "Flake8 complete."

exit ${retval}
