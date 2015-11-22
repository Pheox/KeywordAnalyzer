#!/bin/sh

# create virtualenv:
#	$ virtualenv flask
#	$ source flask/bin/activate
# $ ./create_dev_env.sh

# install DB specific packages:
# 	sudo aptitude install mysql-server
#	sudo apt-get install libmysqlclient-dev
#	sudo aptitude install python-env
#	sudo aptitude install postgresql-server-dev-9.3

pip install -r reqs.txt
