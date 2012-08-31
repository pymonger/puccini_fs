#!/bin/bash

# root directory
ROOT=/data/public

# FUSE mount
MOUNT=/data/public_fuse

# source puccini environment
source $HOME/puccini_env/bin/activate

# stop supervisord
kill -TERM `cat $HOME/puccini_env/run/supervisord.pid`

# unmount puccini filesystem
fusermount -u $MOUNT
