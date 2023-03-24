#!/bin/bash

if [ -z "$IP_SERVER" ];
then
  echo "IP_SERVER must be set"
  exit 1
fi

if [ -z "$DDNS_PROVIDER" ];
then
  echo "DDNS_PROVIDER must be set"
  exit 1
fi

if [ -z "$ACCESS_KEY" ];
then
  echo "ACCESS_KEY must be set"
  exit 1
fi

if [ -z "$ACCESS_SECRET" ];
then
  echo "ACCESS_SECRET must be set"
  exit 1
fi

if [ -z "$DOMAINS" ];
then
  echo "DOMAINS must be set"
  exit 1
fi

if [ -z "$INTERVAL" ];
then
  echo "INTERVAL must be set"
  exit 1
fi

python -u ./ddns.py
