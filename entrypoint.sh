#!/bin/bash

pip3 install --user --upgrade -r /requirements.txt --extra-index-url http://aws:tWC8t4HYu92b@tn-pypi.eu-west-1.elasticbeanstalk.com/pypi --trusted-host tn-pypi.eu-west-1.elasticbeanstalk.com

# Args: username, token, repo_name, pr_number
python main.py -u $1 -t $2 -r $3 -n $4 -o $5
