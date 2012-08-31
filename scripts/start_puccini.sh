#!/bin/bash

# root directory
ROOT=/data/public

# FUSE mount
MOUNT=/data/public_fuse

# source puccini environment
source $HOME/puccini_env/bin/activate

# start up supervisord
cd $HOME
supervisord

# mount puccini filesystem
cd $HOME/puccini_env/log
$HOME/workspace/puccini_fs/puccini_fs $ROOT $MOUNT
