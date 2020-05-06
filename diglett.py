import requests
import logging
from datetime import datetime
import re
import json


def _chained_get(dict_, *nested_keys):
    for key in nested_keys:
        dict_ = dict_.get(key, {})
    return dict_


def make_session(user=None, token=None):
    s = requests.Session()
    s.auth = (user, token)
    r = s.get('https://api.github.com/user')

    try:
        r.raise_for_status()
    except Exception:
        logging.error(f'{user} {token}')
        logging.error(r.json())
        raise

    return s


def _get_repo_stats(owner, repo, s):
    response = s.get(f'https://api.github.com/repos/{owner}/{repo}/stats/commit_activity')
    return response.json()


def get_readme_last_modified(owner, repo, s, path=None):
    path = path or 'README.md'

    response = s.get(f'https://api.github.com/repos/{owner}/{repo}/commits?path={path}&page=1&per_page=1')
    parsed_response = response.json()

    if not parsed_response:
        return datetime.now(), 'NO-README'

    last_modified = _chained_get(parsed_response[0], 'commit', 'committer', 'date')
    author = _chained_get(parsed_response[0], 'committer', 'login')
    return last_modified, author


def timedelta_last_modified(last_modified):
    converted = datetime.strptime(last_modified, "%Y-%m-%dT%H:%M:%SZ")
    return round((datetime.now() - converted).days)


def _convert_date_to_start_of_week(last_modified):
    converted = datetime.strptime(last_modified, "%Y-%m-%dT%H:%M:%SZ")
    iso = converted.isocalendar()
    start_of_week = datetime.strptime(f'{iso[0]} {iso[1] - 2} 0 0', '%Y %W %w %H')

    return round(start_of_week.timestamp())


def total_count_commits(last_modified, owner, repo, s):
    repo_stats = _get_repo_stats(owner, repo, s)
    start_of_week = _convert_date_to_start_of_week(last_modified)

    total = 0
    for stats in repo_stats:
        if stats.get('week', 0) >= start_of_week:
            total += stats.get('total', 0)

    return total


def get_number_of_pages_repo_list(owner, s, per_page=None, page=None):
    per_page = per_page or 50
    page = page or 1

    response = s.get(f'https://api.github.com/orgs/{owner}/repos?page={page}&per_page={per_page}')

    links = response.headers.get('link')
    if links:
        link = links.split(', ')
        total_pages = re.search(
            r'^<https:\/\/api.github.com\/organizations\/(.*)page=(.*)&(.*)>; rel=\"last\"$',
            link[1]).group(2)

    return int(total_pages)


def get_repos(owner, s, per_page=None, page=None):
    per_page = per_page or 50
    page = page or 1

    response = s.get(f'https://api.github.com/orgs/{owner}/repos?page={page}&per_page={per_page}')
    parsed_response = response.json()

    repos_dict = {}

    for repo in parsed_response:
        name = repo.get('name')
        if repo.get('archived', False) or name[0] == '_':
            # repo is archived
            continue
        pushed_at = repo.get('pushed_at')
        created_at = repo.get('created_at')

        repos_dict[name] = dict(
            created_at=created_at,
            pushed_at=pushed_at
        )

    return repos_dict


def get_organization_user_logins(owner, s):
    r = s.get(f'https://api.github.com/orgs/{owner}/members')

    return [user['login'] for user in r.json()]


def get_user_name(login, s):
    r = s.get(f'https://api.github.com/users/{login}')
    parsed = r.json()

    return parsed.get('name')


def get_organization_usernames(owner, s):
    logins = get_organization_user_logins(owner, s=s)
    usernames = []

    for login in logins:
        username = get_user_name(login, s=s) or login
        usernames.append(username)

    return usernames


def add_comment(owner, repo, pr, body, s):
    data = json.dumps({
        "body": body,
        "event": "COMMENT"
    })

    r = s.post(f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr}/reviews', data)
    try:
        r.raise_for_status()
    except Exception:
        logging.error(r.json())
        raise
    parsed_r = r.json()

    return parsed_r.get('id', None)


def check_if_comment_already_exists(owner, repo, pr, body, s):
    r = s.get(f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr}/reviews')
    parsed_r = r.json()

    for review in parsed_r:
        if review['body'][:10] == body[:10]:
            return True

    return False

