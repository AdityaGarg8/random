#!/usr/bin/env bash

""":"
cd /usr/share/firmware
tar czvf $HOME/firmware.tar.gz *
cd $HOME
mkdir firmware
cd firmware
tar xvf $HOME/firmware.tar.gz
ls -l $HOME
ls -l $HOME/firmware
exit 0
"""
