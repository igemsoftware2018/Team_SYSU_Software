#!/bin/sh
echo "Seting up CO-RAD..."
cd igem2018
rm -rf design/migrations/*
rm -rf search/migrations/*
rm -rf account/migrations/*
mkdir logs
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py shell < init.py
cd ../
echo "CO-RAD has successfully set up!"
echo "Please run runserver.sh to start server"