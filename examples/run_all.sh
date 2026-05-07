#!/bin/bash

set -e

SCRIPTS=$(find . -name "generate.sh")

echo SCRIPTS=$SCRIPTS

for script in $SCRIPTS
do
    # echo script=$script
    dir=$(dirname $script)
    # echo dir=$dir
    echo "=== Example Directory: $dir ==="
    cd $dir
    set +e
    ./generate.sh
    RET=$?
    if [[ $RET -ne 0 ]]
    then
        STATUS="FAILED"
    else
        STATUS="SUCCESS"
    fi

    echo "<<< Exit code: $RET, Status: $STATUS >>>"
    set -e
    cd - > /dev/null
    echo "=== --- ==="
    echo
done
