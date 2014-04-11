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
# TODO
# check whether the packages are already installed
sudo apt-get install build-essential python-dev

# option to install required modules
while true; do
    read -e -p "do you want to install the required Python modules? (y/n): " REQUIREMENTS_ANSWER
    case $REQUIREMENTS_ANSWER in
        [Yy]*)
            # TODO
            # make compatible with virtual environments (don't use sudo inside one)
            # http://stackoverflow.com/questions/14695278/python-packages-not-installing-in-virtualenv-using-pip
            sudo pip install -r requirements.txt
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

    ### Configure Package Management System (APT)
    # Import MongoDB PGP key.
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
    # Create a sources.list file for MongoDB.
    echo 'deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
    # Reload local package database.
    sudo apt-get update

    ### Install Packages
    sudo apt-get install mongodb-10gen

    echo "MongoDB successfully installed"
}

# check whether MongoDB is already installed
# http://askubuntu.com/questions/17823/how-to-list-all-installed-packages
# TODO
# simplify the installation check
if ! dpkg --get-selections | grep mongodb &> /dev/null; then
    if ! command -v mongo &> /dev/null; then
        install_mongodb
    fi
fi

### /MongoDB ##################################################################
