import sys
import os
import logging
from diglett import (
    make_session,
    get_readme_last_modified,
    total_count_commits_from_last_modified,
    timedelta_last_modified,
    add_comment,
    get_organization_user_logins,
    check_if_comment_already_exists,
    datetime_readable,
    get_repo_readme_paths,
    get_repo_stats
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
    max_days = env_vars.get('INPUT_MAX_DAYS', 50)
    token = env_vars['INPUT_TOKEN']
    pr_number = env_vars['INPUT_PR_NUMBER']

    session = make_session(token)

    if check_if_comment_already_exists(owner, repo_name, pr_number, s=session):
        print(f"::set-output name=OutputMessage:: Diglett already dug this pull request, digging away!")
        sys.exit(0)

    message = f'![diglett](https://raw.githubusercontent.com/TravelNest/diglett/master/diglett.gif) \n' \
        f'Hello hello, \n' \
        f'I am Diglett and I dig in your documentation! Here is the list of repo `README.md`s \n \n'

    logins = get_organization_user_logins(owner, s=session)
    readme_paths = get_repo_readme_paths(owner, repo_name, session)

    repo_stats = get_repo_stats(owner, repo_name, session)
    is_rm_outdated = []

    for rm in readme_paths:
        last_modified, author = get_readme_last_modified(owner, repo_name, s=session, path=rm)
        number_of_commits = total_count_commits_from_last_modified(repo_stats, last_modified)
        time_delta = timedelta_last_modified(last_modified)

        is_over_max_commit_threshold = int(max_commits) < number_of_commits
        is_author_still_member = author in logins
        is_over_max_days = int(max_days) < time_delta

        is_rm_outdated.append(not (is_over_max_days or not is_author_still_member or is_over_max_commit_threshold))

        author_emoji = 'white_check_mark' if is_author_still_member else 'heavy_exclamation_mark'
        commits_emoji = 'heavy_exclamation_mark' if is_over_max_commit_threshold else 'white_check_mark'
        date_emoji = 'heavy_exclamation_mark' if is_over_max_days else 'white_check_mark'

        author_suffix = f'still member of {owner}' if is_author_still_member else f'**not member of {owner} any more**!'

        message += f'`{rm}` \n' \
            f':{author_emoji}: :bust_in_silhouette: **{author}** last modified the `README.md`, who is {author_suffix}.\n' \
            f':{date_emoji}: :date: It was last modified: {datetime_readable(last_modified)} \n' \
            f':{commits_emoji}: :hash: Since then **{number_of_commits} commits** were pushed \n\n' \

    is_repo_outdated = not all(is_rm_outdated)
    outdated_suffix = f'Your repo documentation is outdated' if is_repo_outdated else \
        'Update your `README.md` and keep the repo up to dated!'
    message += f':memo: {outdated_suffix} \n' \

    print(f"::set-output name=OutputMessage:: Is repo outdated? {is_repo_outdated}")
    logging.error(message)

    add_comment(owner, repo_name, pr_number, message, s=session)

    sys.exit(0)


if __name__ == "__main__":
    main()
