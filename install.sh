#!/usr/bin/env bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

function install_pkg () {
    local PKG=$1

    echo "Installing package '$PKG'."

    if [[ $(rpm -qa | grep "$PKG") ]]; then
        echo "Package '$PKG' already installed. Skipping."
        return
    fi

    if [[ ! $(sudo -E yum install -y "$PKG") ]]; then
        echo >&2 "Failed to install '$PKG'. Aborting."
        exit 1
    else
        echo "Package '$PKG' installed successfully."
    fi
}

function install_packages () {
    local PKGS=$(cat $1)

    for PKG in $PKGS; do
        install_package "$PKG"
    done
}

function install_requirements () {
    local REQ_FILE=$1

    echo "Installing Python requirements from '$REQ_FILE'."

    if [[ ! $(pip install -r "$REQ_FILE") ]]; then
        echo "Failed to install requirements via pip. Aborting."
        exit 1
    else
        echo "Python requirements installed successfully."
    fi
}

install_packages "$ROOT_DIR/packages.txt"
install_requirements "$ROOT_DIR/requirements.txt"
