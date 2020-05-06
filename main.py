import sys
import os
import logging
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
    vars = os.environ
    required_vars = ['INPUT_USERNAME', 'INPUT_PR_NUMBER', 'INPUT_TOKEN']

    if all(v in required_vars and vars[v] for v in vars):
        # All parameters are required
        logging.error(f'Some of the required parameter is missing: {vars}')
        print(f"::set-output name=OutputMessage:: Some of the required parameter is missing: {vars}")
        sys.exit(1)

    owner = vars['GITHUB_REPOSITORY_OWNER']
    repo_name = vars['GITHUB_REPOSITORY'].split('/', 1)[1]
    max_commits = vars.get('INPUT_MAX_COMMITS', 100)
    max_days = 50
    username = vars['INPUT_USERNAME']
    token = vars['INPUT_TOKEN']
    pr_number = vars['INPUT_PR_NUMBER']

    session = make_session(username, token)

    logins = get_organization_user_logins(owner, s=session)
    last_modified, author = get_readme_last_modified(owner, repo_name, s=session)
    num_commits = total_count_commits(last_modified, owner, repo_name, s=session)
    time_delta = timedelta_last_modified(last_modified)

    is_over_threshold = int(max_commits) < num_commits
    is_author_still_member = author in logins
    is_outdated = max_days < time_delta

    is_repo_outdated = (is_outdated and is_author_still_member and is_over_threshold)

    author_emoji = 'white_check_mark' if is_author_still_member else 'heavy_exclamation_mark'
    commits_emoji = 'heavy_exclamation_mark' if is_over_threshold else 'white_check_mark'
    date_emoji = 'heavy_exclamation_mark' if is_outdated else 'white_check_mark'

    author_suffix = f'still member of {owner}' if is_author_still_member else f'**not member of {owner} any more**!'

    message = f'![diglett](https://raw.githubusercontent.com/TravelNest/diglett/master/diglett.gif) \n'\
        f'Hello hello, \n' \
        f'I am Diglett and I dig for your documentation outdatedness! \n \n' \
        f':{author_emoji}: :bust_in_silhouette: **{author}** last modified the `README.md`, who is {author_suffix}.\n' \
        f':{date_emoji}: :date: `README.md` was last modified: {last_modified} \n' \
        f':{commits_emoji}: :hash: Since then **{num_commits} commits** where pushed \n\n' \
        f':memo: Update your `README.md` to prevent it being outdated! \n' \

    print(f"::set-output name=OutputMessage:: Is repo outdated? {is_repo_outdated}")
    logging.info(message)

    if not check_if_comment_already_exists(owner, repo_name, pr_number, message, s=session):
        add_comment(owner, repo_name, pr_number, message, s=session)

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
