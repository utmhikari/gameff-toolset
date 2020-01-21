import logger
import os
import json
import git
from git.repo import Repo

LOGGER = logger.get_logger('GIT_REPO_MANAGER')


class GitRepoManager:
    """
    git repo manager
    based on GitPython (see https://gitpython.readthedocs.io/en/stable/intro.html)
    manage git repos, offer apis for other services
    repo path template: $root_dir/$domain_name/$repo_name
    """
    def __init__(self,
                 root_dir='./tmp/git_repos',
                 default_ssh_key=''):
        self._root_dir = root_dir
        self._default_ssh_key = default_ssh_key
        if not os.path.isdir(root_dir):
            os.makedirs(root_dir, exist_ok=True)

    def info_all(self):
        """
        all info of repos as string
        :return: info of all repos
        """
        info = []
        domain_list = os.listdir(self._root_dir)
        for domain in domain_list:
            d = os.path.join(self._root_dir, domain)
            if os.path.isdir(d):
                repo_list = os.listdir(d)
                for repo in repo_list:
                    r = os.path.join(d, repo)
                    if os.path.isdir(r):
                        info.append({
                            'domain': domain,
                            'name': repo,
                        })
        return info


if __name__ == '__main__':
    manager = GitRepoManager('./test/git_repos')
    print(json.dumps(manager.info_all()))