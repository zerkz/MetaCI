#!/bin/bash
# This script runs the tests on Heroku CI

git clone -b "$HEROKU_TEST_RUN_BRANCH" --single-branch https://github.com/SFDO-Tooling/MetaCI MetaCI_checkout 
cd MetaCI_checkout
git reset --hard $HEROKU_TEST_RUN_COMMIT_VERSION
export DJANGO_SETTINGS_MODULE=config.settings.test

# Enable coveralls parallel mode so we can report for both Python & JS
export COVERALLS_PARALLEL=true
# Coveralls doesn't recognize the Heroku CI environment automatically.
# So let's pretend we're CircleCI.
export CIRCLECI=true
export CIRCLE_BUILD_NUM=$HEROKU_TEST_RUN_ID

# Run webpack to build frontend assets
# (the buildpack does this, but not in the MetaCI_checkout directory)
yarn prod

# Run Python tests
coverage run $(which pytest) --tap-stream
exit_status=$?
coveralls

# Run JS tests
yarn test:coverage
exit_status=$exit_status || $?
cat ./coverage/lcov.info | /app/node_modules/.bin/coveralls

curl -k "https://coveralls.io/webhook?repo_token=${COVERALLS_REPO_TOKEN}" -d "payload[build_num]=${HEROKU_TEST_RUN_ID}&payload[status]=done"
if [ "$exit_status" != "0" ]; then
    exit $exit_status
fi
