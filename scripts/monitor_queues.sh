#!/bin/sh
clear
status=`sudo rabbitmqctl list_queues`
while [ 1 ]; do
  echo "$status"
  sleep 1
  status=`sudo rabbitmqctl list_queues`
  clear
done
