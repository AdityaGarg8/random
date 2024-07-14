#!/bin/bash

# Switching to root
sudo $0

if [ "$EUID" -ne 0 ]; then
    exit 1
fi

# Detecting Package Manager
PM_INSTALL=""
PM_REMOVE="null"

if apt --help >/dev/null 2>&1; then
    echo "Debian-based OS are not supported!"
    echo "Please use 'sudo touchbar --switch' instead."
#    exit 1
elif dnf >/dev/null 2>&1; then
    echo "Fedora-based OS are not supported!"
    exit 1
elif pacman -h >/dev/null 2>&1; then
    PM_INSTALL="pacman -Sy"
    PM_REMOVE="pacman -Rnsu"
else
    echo "No valid package manager has been found!"
    exit 1
fi

# Checking dependencies
echo "Cheking dependencies..."

if ! command -v git &>/dev/null; then # GIT
    echo "git could not be found! Installing..."
    $PM_INSTALL git
fi

if ! command -v dkms &>/dev/null; then # DKMS
    echo "dkms could not be found! Installing..."
    $PM_INSTALL dkms
fi

# SWITCH TO OLD DRIVER
if [[ "$1" == "--old" ]]; then

    # Switching to old driver
    echo "Switching to old driver..."

    # Removing tiny-dfr
#    $PM_REMOVE tiny-dfr

    # Blacklisting new driver
    echo "Blacklisting new touchbar driver..."

    cat <<- EOF > /etc/modprobe.d/touchbar.conf
    # Disable new Apple Touchbar driver
    blacklist appletbdrm
    blacklist hid_appletb_kbd
    blacklist hid_appletb_bl
    EOF

    # Installing old driver
    echo "Cloning driver repo..."
    git clone https://github.com/AdityaGarg8/apple-touchbar-drv /usr/src/apple-touchbar-0.1
    dkms install -m apple-touchbar -v 0.1

# SWITCH TO NEW DRIVER
elif [[ "$1" == "--new" ]]; then

    # Switching to new driver
    echo "Switching to new driver..."

    # Installing tiny-dfr
    $PM_INSTALL tiny-dfr

    # Removing blacklist conf
    rm /etc/modprobe.d/touchbar.conf

    # Removing old driver
    dkms unbuild -m apple-touchbar -v 0.1 -k all
    rm -r /usr/src/apple-touchbar-0.1

else

    echo "Choose a valid option:"
    echo "--new (Switches to the new driver)"
    echo "--old (Switches to the old driver)"
    exit 1

fi

# DONE!
echo "All done! You can now reboot..."
read -p "Do you want to reboot now? [y/N]" -n 1 -r -s
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Rebooting..."
    reboot
fi
