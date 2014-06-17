#!/bin/bash

# The actual cron jobs are echo'd into a variable
# app_cron towards the end

START_TOKEN="# START PODCASTQUOTES CRON JOBS"
END_TOKEN="# END PODCASTQUOTES CRON JOBS"

function crontab_exists () {
   crontab -l
}

function get_full_dir() {
    # Obtain pull path
    pushd "$1" > /dev/null
    SCRIPTPATH=`pwd`
    popd > /dev/null
    
    echo "${SCRIPTPATH}"
}

function remove_app_cron () {
    awk "/${START_TOKEN}/ { d = 1} { if (d != 1) { print \$0 } } /${END_TOKEN}/ { d = 0}"
}

function help () {
    
    echo
    echo "Usage: $0 django_project_path virtualenv_path"
    
}

#
## Start Script
#

# Arg-checks

if ! test -d "$1"; then
    echo 'You need to provide the full path to django_project.'
    help
    exit 1
fi

if ! test -e "$2/bin/activate"; then
    echo 'You need to provide the full path a valid virtualenv.'
    help
    exit 1
fi

DJANGO_PROJECT="$1"
MANAGE_PY="source ${2}/bin/activate && ${DJANGO_PROJECT}/manage.py"

#
#- Obtain current crontab
#
if ! crontab_exists; then
    crontab=''
else
    crontab=$(crontab -l | remove_app_cron)
fi

# The cronjobs that this app should register
app_cron=$(
    echo "${START_TOKEN}"

    # Rank quotes every minute
    echo "* * * * * /bin/bash -c '${MANAGE_PY} rank_quotes'"

    # Update RSS Feeds in the middle of the night.
    echo "0 3 * * * /bin/bash -c '${MANAGE_PY} update_rss_feeds'"

    echo "${END_TOKEN}"
)

# Install into crontab

power=$(echo "${crontab}"; echo "${app_cron}")
echo "${power}" | crontab -
