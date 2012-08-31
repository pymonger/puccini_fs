#!/bin/bash

# root directory
ROOT=/data/public

# FUSE mount
MOUNT=/data/public_fuse

# source puccini environment
source $HOME/puccini_env/bin/activate

# stop supervisord
kill -TERM `cat $HOME/puccini_env/run/supervisord.pid`
sleep 30

# unmount puccini filesystem
fusermount -u $MOUNT

# clean out solr database
rm -rf $HOME/workspace/pysolr/solr/solr_example/solr/data

# clean out root
rm -rf $ROOT/* $ROOT/.DS* $ROOT/._*

# start up supervisord
cd $HOME
supervisord

# mount puccini filesystem
cd $HOME/puccini_env/log
$HOME/workspace/puccini_fs/puccini_fs $ROOT $MOUNT
