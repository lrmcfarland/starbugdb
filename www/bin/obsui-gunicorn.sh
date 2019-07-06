#!/usr/bin/env bash

# see also https://github.com/lrmcfarland/AAI/blob/master/www/bin/aai-gunicorn.sh

# TODO more args? https://stackoverflow.com/questions/36346550/gunicorn-failed-to-load-flask-application?rq=1

# I tried a bunch of things to pass both the gunicorn and flask config files:
# I decided to use an environment variable OBSUI_FLASK_CONFIG for now.

# ----------------------
# ----- parse args -----
# ----------------------

# cli args from http://mywiki.wooledge.org/BashFAQ/035#getopts

show_help() {
cat << EOF
Usage: ${0##*/} [-h] [-f FLASK CONFIG FILE] [-g GUNICORN CONFIG FILE]

Passes a flask config file to the AAI flask framework and a gunicorn
config file to the gunicorn framework.

    -h                       display this help and exit
    -f FLASK_CONFIG_FILE     Flask configuration file
    -g GUNICORN_CONFIG_FILE  Gunicorn configuration file

EOF
}

die() {
    printf '%s\n' "$1" >&2
    exit 1
}

# Initialize all the option variables.
# This ensures we are not contaminated by variables from the environment.

gunicorn_config_file=
flask_config_file=


while :; do
    case $1 in
	-h|-\?|--help)
	    show_help    # Display a usage synopsis.
	    exit
	    ;;


	-f|--flask-file)       # Takes an option argument; ensure it has been specified.
	    if [ "$2" ]; then
		flask_config_file=$2
		shift
	    else
		die 'ERROR: "--flask-file" requires a non-empty option argument.'
	    fi
	    ;;
	--flask-file=?*)
	    flask_config_file=${1#*=} # Delete everything up to "=" and assign the remainder.
	    ;;
	--flask-file=)         # Handle the case of an empty --file=
	    die 'ERROR: "--flask-file" requires a non-empty option argument.'
	    ;;


	-g|--gunicorn-file)       # Takes an option argument; ensure it has been specified.
	    if [ "$2" ]; then
		gunicorn_config_file=$2
		shift
	    else
		die 'ERROR: "--gunicorn-file" requires a non-empty option argument.'
	    fi
	    ;;
	--gunicorn-file=?*)
	    gunicorn_config_file=${1#*=} # Delete everything up to "=" and assign the remainder.
	    ;;
	--gunicorn-file=)         # Handle the case of an empty --file=
	    die 'ERROR: "--gunicorn-file" requires a non-empty option argument.'
	    ;;


	-?*)
	    printf 'WARN: Unknown option (ignored): %s\n' "$1" >&2
	    ;;
	*)               # Default case: No more options, so break out of the loop.
	    break
    esac

    shift
done


if [ -z "$flask_config_file" ]; then
    echo '# OBSUI warning: no flask config file provided.'
    echo '# OBSUI_FLASK_CONFIG:' $OBSUI_FLASK_CONFIG
else
    echo '# OBSUI gunicorn wrapper ignoring flask config file:' $flask_config_file
fi


if [ -z "$gunicorn_config_file" ]; then
    die 'OBSUI ERROR: a gunicorn config file is required'
else
    echo '# OBSUI gunicorn config file:' $gunicorn_config_file
fi

echo '#' # linefeed

# ===========================
# ===== run application =====
# ===========================

echo "# Starting gunicorn with config file: "  $gunicorn_config_file

echo "PYTHONPATH = " $PYTHONPATH

gunicorn -c $gunicorn_config_file "gobsui"
