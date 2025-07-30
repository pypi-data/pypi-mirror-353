#!/bin/bash

ports=(6277 6274)

for port in "${ports[@]}"; do
  pid=$(lsof -ti tcp:$port)
  if [ -n "$pid" ]; then
    echo "Killing process $pid on port $port"
    kill -9 $pid
  else
    echo "No process found on port $port"
  fi
done
