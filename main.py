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
    check_if_comment_already_exists,
    datetime_readable
)


# TODO: pr_number can be parsed from vars['GITHUB_REF'] = 'refs/pull/3/merge'
def main():
    env_vars = os.environ
    required_vars = ['INPUT_USERNAME', 'INPUT_PR_NUMBER', 'INPUT_TOKEN']

    if all(v in required_vars and env_vars[v] for v in env_vars):
        # All parameters are required
        logging.error(f'Some of the required parameters is missing: {env_vars}')
        print(f"::set-output name=OutputMessage:: Some of the required parameters is missing: {env_vars}")
        sys.exit(1)

    owner = env_vars['GITHUB_REPOSITORY_OWNER']
    repo_name = env_vars['GITHUB_REPOSITORY'].split('/', 1)[1]
    max_commits = env_vars.get('INPUT_MAX_COMMITS', 100)
    max_days = 50
    username = env_vars['INPUT_USERNAME']
    token = env_vars['INPUT_TOKEN']
    pr_number = env_vars['INPUT_PR_NUMBER']

    session = make_session(username, token)

    if check_if_comment_already_exists(owner, repo_name, pr_number, s=session):
        print(f"::set-output name=OutputMessage:: Diglett already dug this pull request, digging away!")
        sys.exit(0)

    logins = get_organization_user_logins(owner, s=session)
    last_modified, author = get_readme_last_modified(owner, repo_name, s=session)
    num_commits = total_count_commits(last_modified, owner, repo_name, s=session)
    time_delta = timedelta_last_modified(last_modified)

    is_over_max_commit_threshold = int(max_commits) < num_commits
    is_author_still_member = author in logins
    is_over_max_days = max_days < time_delta

    is_repo_outdated = (is_over_max_days or not is_author_still_member or is_over_max_commit_threshold)

    author_emoji = 'white_check_mark' if is_author_still_member else 'heavy_exclamation_mark'
    commits_emoji = 'heavy_exclamation_mark' if is_over_max_commit_threshold else 'white_check_mark'
    date_emoji = 'white_check_mark' if is_over_max_days else 'heavy_exclamation_mark'

    author_suffix = f'still member of {owner}' if is_author_still_member else f'**not member of {owner} any more**!'
    outdated_suffix = f'Your repo documentation is outdated' if is_repo_outdated else \
        'Update your `README.md` to prevent it being outdated!'

    message = f'![diglett](https://raw.githubusercontent.com/TravelNest/diglett/master/diglett.gif) \n'\
        f'Hello hello, \n' \
        f'I am Diglett and I dig in your documentation! \n \n' \
        f':{author_emoji}: :bust_in_silhouette: **{author}** last modified the `README.md`, who is {author_suffix}.\n' \
        f':{date_emoji}: :date: `README.md` was last modified: {datetime_readable(last_modified)} \n' \
        f':{commits_emoji}: :hash: Since then **{num_commits} commits** were pushed \n\n' \
        f':memo: {outdated_suffix} \n' \

    print(f"::set-output name=OutputMessage:: Is repo outdated? {is_repo_outdated}")
    logging.error(message)

    add_comment(owner, repo_name, pr_number, message, s=session)

    sys.exit(0)


if __name__ == "__main__":
    main()
