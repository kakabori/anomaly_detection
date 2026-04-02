#!/bin/bash

MACHINE_ID=${1:-"001"}

curl -X POST http://127.0.0.1:5000/diagnose \
  -H "Content-Type: application/json" \
  -d "{\"machineid\": \"$MACHINE_ID\"}"