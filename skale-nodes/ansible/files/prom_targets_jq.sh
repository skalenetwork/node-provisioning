#!/bin/bash

IPS=($( jq -r '[.[]]|join(" ")' $1 ))

echo -n '    - targets: ['
for IP in ${IPS[@]}
do
  echo -n "'$IP:9144',"
  echo -n "'$IP:9256'"
  if [ "$IP" != "${IPS[-1]}" ]
  then
    echo -n ','
  fi
done
echo ']'