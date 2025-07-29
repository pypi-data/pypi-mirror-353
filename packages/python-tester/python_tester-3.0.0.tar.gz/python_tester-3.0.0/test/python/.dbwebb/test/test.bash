#!/usr/bin/env bash

# Setting up
python3 --version >/dev/null 2>&1 && py=python3 || py=python

# Setting a base path
SCRIPT_PATH=`realpath $0`
DBWEBB_TEST_DIR=`dirname "$SCRIPT_PATH"`
LOG_PATH="${DBWEBB_TEST_DIR}/.test-log"

cp -r "$DBWEBB_TEST_DIR/../../../../build/examiner" "$DBWEBB_TEST_DIR/"

# What kmom / assignment to test
CURRENT_DIR=$(pwd | awk -F/ '{print $NF}')
WHAT=${1:-$CURRENT_DIR}
ARGUMENTS="${@:2}"

if [[ $WHAT == -* ]]
then
    ARGUMENTS=$1
    WHAT=$CURRENT_DIR
fi

PYTHON_TESTS_PATH=$(find "${DBWEBB_TEST_DIR}" -name "${WHAT}" -and -type d)

if [ -z ${PYTHON_TESTS_PATH} ]
then
    echo "${WHAT} is not a valid test directory"
    exit 1
fi


cd $DBWEBB_TEST_DIR && $py -m examiner.run_tests --what=$PYTHON_TESTS_PATH $ARGUMENTS
