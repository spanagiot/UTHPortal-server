#!/bin/bash

# setup.sh
# setup a development environment for the UTHPortal server


### verify that the script is run in a Debian system or a derivative
if ! command -v dpkg &> /dev/null; then
    echo "error: the UTHPortal setup script should be run on a Debian system or a derivative, such as Ubuntu and Kubuntu, exiting."
    exit 1
fi


### Python and modules ########################################################

# install Python 2.7
if ! command -v python2.7 &> /dev/null; then
    echo "installing Python 2.7"
    sudo apt-get install python2.7
fi
# install pip
if ! command -v pip &> /dev/null; then
    echo "installing pip"
    sudo apt-get install python-pip
fi

# install dependencies of gevent
if ! dpkg --get-selections | grep build-essential &> /dev/null; then
    sudo apt-get install build-essential
fi
if ! dpkg --get-selections | grep python-dev &> /dev/null; then
    sudo apt-get install python-dev
fi

# option to install required modules
while true; do
    read -e -p "do you want to install the required Python modules? (y/n): " REQUIREMENTS_ANSWER
    case $REQUIREMENTS_ANSWER in
        [Yy]*)
            # run pip without sudo inside a virtual environment
            # http://stackoverflow.com/questions/15454174/how-can-a-shell-function-know-if-it-is-running-within-a-virtualenv
            python -c 'import sys; print sys.real_prefix' &> /dev/null && IN_VIRTUAL_ENVIRONMENT=true || IN_VIRTUAL_ENVIRONMENT=false
            # http://stackoverflow.com/questions/2953646/how-to-declare-and-use-boolean-variables-in-shell-script
            if [ "$IN_VIRTUAL_ENVIRONMENT" == true ]; then
                pip install -r requirements.txt
            else
                sudo pip install -r requirements.txt
            fi
            break
            ;;
        [Nn]*)
            break
            ;;
        *)
            echo "please enter \"y\" for yes or \"n\" for no"
            ;;
    esac
done

### /Python and modules #######################################################


### MongoDB ###################################################################

### install MongoDB
install_mongodb() {
    # http://docs.mongodb.org/manual/tutorial/install-mongodb-on-debian/

    echo "installing MongoDB"

    # Import the public key used by the package management system.
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
    # Create a /etc/apt/sources.list.d/mongodb.list file for MongoDB.
    echo 'deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
    # Reload local package database.
    sudo apt-get update
    # Install the MongoDB packages.
    sudo apt-get install mongodb-org

    echo "MongoDB successfully installed"
}

# check whether MongoDB is already installed
# http://askubuntu.com/questions/17823/how-to-list-all-installed-packages
# NOTE
# this test works for now, but it could lead to false positives
if ! dpkg --get-selections | grep mongodb &> /dev/null; then
    install_mongodb
fi

### /MongoDB ##################################################################
