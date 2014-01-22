#!/bin/bash

INSTALL_APTITUDE=true
INSTALL_PIP=true
INSTALL_HEROKU=false
while getopts “ahp” OPTION
do
    case $OPTION in
        a)
             echo "only install aptitude"
             INSTALL_APTITUDE=true
             INSTALL_PIP=false
             INSTALL_HEROKU=false
             ;;
        p)
             echo "only pip install"
             INSTALL_APTITUDE=false
             INSTALL_PIP=true
             INSTALL_HEROKU=false
             ;;
        h)
             echo "only heroku install"
             INSTALL_APTITUDE=false
             INSTALL_PIP=false
             INSTALL_HEROKU=true
             ;;
        ?)
             echo "fail"
             exit
             ;;
     esac
done

if  $INSTALL_NODE ; then
    echo "Installing bower (Requires Node)"
    sudo npm install -g bower
fi

if  $INSTALL_APTITUDE ; then
    echo "Installing aptitude dependencies"

    # Install base packages
    yes | sudo apt-get install python-pip python-virtualenv python-dev 

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
source .env/bin/activate
if [[ "$INSTALL_MYSQL" == "y" ]]
then
    pip install MySQL-python
elif [[ "$INSTALL_POSTGRES" == "y" ]]
then
    pip install psycopg2
fi

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
if [ ! -f ./config/local_settings.py ] ; then
    cp config/local_settings.py.default config/local_settings.py

    EXP="s/database-name/${PWD##*/}/g"
    echo $i|sed -i $EXP config/local_settings.py
    
    echo "remember to set in config/local_setings.py your database"
    echo "settings"
fi

# bower.json modification
EXP="s/NAME/${PWD##*/}/g"
echo $i|sed -i $EXP base/static/bower.json
EXP="s/HOMEPAGE/https:\/\/bitbucket.org\/magnet-cl\/${PWD##*/}/g"
echo $i|sed -i $EXP base/static/bower.json

cd base/static
bower install
cd ../..
