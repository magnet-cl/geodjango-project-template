#!/bin/bash

INSTALL_APTITUDE=true
INSTALL_PIP=true
INSTALL_HEROKU=false
INSTALL_BOWER=true
INSTALL_NPM=true
while getopts “nahpb” OPTION
do
    case $OPTION in
        a)
             echo "only install aptitude"
             INSTALL_APTITUDE=true
             INSTALL_PIP=false
             INSTALL_HEROKU=false
             INSTALL_BOWER=false
             INSTALL_NPM=false
             ;;
        p)
             echo "only pip install"
             INSTALL_APTITUDE=false
             INSTALL_PIP=true
             INSTALL_HEROKU=false
             INSTALL_BOWER=false
             INSTALL_NPM=false
             ;;
        h)
             echo "only heroku install"
             INSTALL_APTITUDE=false
             INSTALL_PIP=false
             INSTALL_HEROKU=true
             INSTALL_BOWER=false
             INSTALL_NPM=false
             ;;
        b)
             echo "only bower install"
             INSTALL_APTITUDE=false
             INSTALL_PIP=false
             INSTALL_HEROKU=false
             INSTALL_BOWER=true
             INSTALL_NPM=false
             ;;
        n)
             echo "only node install"
             INSTALL_APTITUDE=false
             INSTALL_PIP=false
             INSTALL_HEROKU=false
             INSTALL_BOWER=false
             INSTALL_NPM=true
             ;;
        ?)
             echo "fail"
             exit
             ;;
     esac
done

if  $INSTALL_APTITUDE ; then
    echo "Installing aptitude dependencies"

    # Install base packages
    yes | sudo apt-get install python-pip python-virtualenv python-dev 
    
    # Install image libs
    yes | sudo apt-get install libjpeg-dev zlib1g-dev zlib1g-dev

    ./install/postgres.sh

    echo "Do you want to install geodjango requirements? [Y/n]"
    read INSTALL_GEODJANGO_REQ

    if [[ $INSTALL_GEODJANGO_REQ == '' ]]
    then
        # set the default value for the option
        INSTALL_GEODJANGO_REQ="Y"
    fi

    if [[ $INSTALL_GEODJANGO_REQ == 'Y' || $INSTALL_GEODJANGO_REQ == 'y' ]]
    then
        export INSTALL_POSTGRES
        ./install/geodjango_requirements.sh
    fi

    if [ ! -f .env ] ; then
        # set a new virtual environment
        virtualenv .env
    fi
fi

if  $INSTALL_PIP ; then
    # activate the environment
    source .env/bin/activate

    # install setuptools
    pip install --upgrade setuptools

    # install pip requiredments in the virtual environment
    .env/bin/pip install --download-cache=~/.pip-cache --requirement install/requirements.pip

    pip install psycopg2

fi

# update pip database requirements
pip install psycopg2

# HEROKU 
if  $INSTALL_HEROKU ; then
    # activate the environment
    source .env/bin/activate

    wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
    heroku login
    pip install psycopg2 dj-database-url
    pip freeze > requirements.txt
    pip uninstall psycopg2 dj-database-url

    echo "web: python manage.py runserver 0.0.0.0:$PORT --noreload" > Procfile

    echo "Would you like to create a new heroku repo? [N/y]"
    read CREATE_REPO

    if [[ "$CREATE_REPO" == "y" ]]
    then
        heroku create
    fi

    echo "You should now commit the requirements.txt file."
    echo "Then deploy to heroku: git push heroku master"
fi

# create the local_settings file if it does not exist
if [ ! -f ./project/local_settings.py ] ; then
    cp project/local_settings.py.default project/local_settings.py

    EXP="s/database-name/${PWD##*/}/g"
    echo $i|sed -i $EXP project/local_settings.py
    
    echo "remember to set in project/local_setings.py your database"
    echo "settings"
fi

# Change the project/settings.py file it contains the CHANGE ME string
if grep -q "CHANGE ME" "project/settings.py"; then
    # change the SECRET_KEY value on project settings
    python manage.py generatesecretkey
fi


if  $INSTALL_NPM ; then
    npm install
fi

if  $INSTALL_BOWER ; then
    # bower.json modification
    EXP="s/NAME/${PWD##*/}/g"
    echo $i|sed -i $EXP bower.json
    EXP="s/HOMEPAGE/https:\/\/bitbucket.org\/magnet-cl\/${PWD##*/}/g"
    echo $i|sed -i $EXP bower.json

    ./node_modules/bower/bin/bower install
fi
