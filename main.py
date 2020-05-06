import sys
import os
import logging
from getopt import getopt, GetoptError
from diglett import (
    make_session,
    get_readme_last_modified,
    total_count_commits,
    timedelta_last_modified,
    add_comment,
    get_organization_user_logins,
    check_if_comment_already_exists
)


def main(argv):
    try:
        opts, args = getopt(argv, "u:t:o:r:n:h", ["username=", "token=", "owner=" "repo_name=", "pr_number=", "help"])
    except GetoptError:
        print(f"::set-output name=OutputMessage::Got error: {opts}, {args}")
        sys.exit(1)

    username, token, owner, repo_name, pr_number, max_commits, max_days = None, None, None, None, None, 50, 100

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(f'::set-output name=OutputMessage::'
                  f'usage: python main.py [-u username | -t token | -r repo_name | -n pr_number | -h] \n'
                  f'Options and arguments: \n'
                  f'-u, --username     Username to login GitHub API \n'
                  f'-t, --token        Token corresponding to --username to login GitHub API \n'
                  f'-o, --owner        Repository owner or organization \n'
                  f'-r, --repo_name    GitHub repository name \n'
                  f'-n, --pr_number    Pull Request number \n'
                  f'-c, --max_commits  Threshold for max. number of commits accepted \n'
                  f'-h                 Help\n'
            )
            sys.exit(0)
        elif opt in ("-u", "--username"):
            username = arg
        elif opt in ("-t", "--token"):
            token = arg
        elif opt in ("-o", "--owner"):
            owner = arg
        elif opt in ("-r", "--repo_name"):
            repo_name = arg
        elif opt in ("-c", "--max_commits"):
            max_commits = arg
        elif opt in ("-n", "--pr_number"):
            pr_number = arg

    if not username or not token or not owner or not repo_name or not pr_number:
        # All parameters are required
        logging.error(f'Some of the required parameter is missing: {opts}, {args}, {os.environ}')
        print(f"::set-output name=OutputMessage:: Some of the required parameter is missing: {opts}, {args}")
        sys.exit(1)

    session = make_session(username, token)

    logins = get_organization_user_logins(owner, s=session)
    last_modified, author = get_readme_last_modified(owner, repo_name, s=session)
    num_commits = total_count_commits(last_modified, owner, repo_name, s=session)
    time_delta = timedelta_last_modified(last_modified)

    is_over_threshold = max_commits < num_commits
    is_author_still_member = author in logins
    is_outdated = max_days < time_delta

    author_emoji = 'white_check_mark' if is_author_still_member else 'heavy_exclamation_mark'
    commits_emoji = 'heavy_exclamation_mark' if is_over_threshold else 'white_check_mark'
    date_emoji = 'heavy_exclamation_mark' if is_outdated else 'white_check_mark'

    author_suffix = f'still member of {owner}' if is_author_still_member else f'**not member of {owner} any more**!'

    message = f'![diglett](https://github.com/TravelNest/diglett/blob/master/diglett.gif) \n'\
        f'Hello hello, \n' \
        f'I am Diglett and I dig for your documentation outdatedness! \n \n' \
        f':{author_emoji}: :bust_in_silhouette: **{author}** last modified the `README.md`, who is {author_suffix}.\n' \
        f':{date_emoji}: :date: `README.md` was last modified: {last_modified} \n' \
        f':{commits_emoji}: :hash: Since then **{num_commits} commits** where pushed \n\n' \
        f':memo: Update your `README.md` to prevent it being outdated! \n' \

    print(f"::set-output name=OutputMessage::{message}")
    logging.info(message)

    if not check_if_comment_already_exists(owner, repo_name, pr_number, message, s=session):
        add_comment(owner, repo_name, pr_number, message, s=session)

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
