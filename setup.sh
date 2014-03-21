#!/bin/bash

# setup.sh
# setup the UTHPortal server


### verify that the script is run in a Debian system or a derivative
if ! command -v dpkg &> /dev/null; then
    echo "error: the UTHPortal setup script should be run on a Debian system or a derivative, such as Ubuntu and Kubuntu, exiting."
    exit 1
fi


### MongoDB ###################################################################

### install MongoDB
install_mongodb() {
    # http://docs.mongodb.org/manual/tutorial/install-mongodb-on-debian/

    echo
    echo "MongoDB installation"
    echo

    ### Configure Package Management System (APT)
    # Import MongoDB PGP key.
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
    # Create a sources.list file for MongoDB.
    echo 'deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
    # Reload local package database.
    sudo apt-get update

    ### Install Packages
    sudo apt-get install mongodb-10gen

    echo
    echo "MongoDB successfully installed"
    echo
}

# check whether MongoDB is already installed
# http://askubuntu.com/questions/17823/how-to-list-all-installed-packages
if ! dpkg --get-selections | grep mongodb &> /dev/null; then
    install_mongodb
else
    echo
    echo "MongoDB is already installed (probably :P )"
    echo
fi

### /MongoDB ##################################################################
