#!/usr/bin/env bash

""":"
cd /usr/share/firmware
tar czvf $HOME/firmware.tar.gz *
cd $HOME
tar xvf $HOME/firmware.tar.gz
ls -l $HOME
exit 0
"""
