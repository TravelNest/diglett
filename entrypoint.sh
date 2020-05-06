#!/bin/sh

# Args: username, token, repo_name, pr_number
echo `python main.py -u $1 -t $2 -r $3 -n $4 -o $5 -c $6`
