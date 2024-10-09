#!/bin/bash
cd bootstrap
helm dependency update
cd ..
helm upgrade --install bootstrap bootstrap
sleep 20
cd databases
helm dependency update
cd ..
helm upgrade --install databases databases
sleep 120
helm upgrade --install application application