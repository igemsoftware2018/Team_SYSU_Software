@echo Seting up S-din...
@cd igem2018
@RD /S /Q  search\migrations
@RD /S /Q  design\migrations
@RD /S /Q  account\migrations
@python3 manage.py makemigrations sdin
@IF %ERRORLEVEL% NEQ 0 goto error
@python3 manage.py migrate
@IF %ERRORLEVEL% NEQ 0 goto error 
@python3 manage.py shell < init.py
@IF %ERRORLEVEL% NEQ 0 goto error
@cd ..\
@echo CO-RAD has successfully set up!
@echo Please run runserver.sh to start server
@pause
@exit

error:
@echo Set up failed...Closing...
@pause
@exit