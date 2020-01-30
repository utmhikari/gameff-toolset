import logger
import os
import json
import git
import util
from typing import Dict, List
from collections.abc import Iterable
import time


LOGGER = logger.get_logger('GIT_REPO_MANAGER')


class GitRepoManager:
    """
    git repo manager
    based on GitPython (see https://gitpython.readthedocs.io/en/stable/intro.html)
    manage git repos, offer apis for other services
    repo path template: $root_dir/$domain_name/$repo_name
    configure GIT_PYTHON_GIT_EXECUTABLE env var before use
    """
    def __init__(self, root_dir: str = './tmp/git_repos'):
        self._root_dir: str = root_dir
        if not os.path.isdir(root_dir):
            os.makedirs(root_dir, exist_ok=True)
        self._info: Dict[str, git.Repo] = dict()
        self._load()
        LOGGER.info('Loaded git repos:\n%s' % util.ppf(self.get_info(), is_json=True))

    def _clone(self, git_url: str, branch: str = 'master', ssh_key: str = ''):
        """
        :param git_url: git url
        :param branch: branch
        :param ssh_key: ssh key
        :return:
        """
        hs = GitRepoManager._hash(git_url)
        dest = os.path.join(self._root_dir, hs)
        repo = git.Repo.clone_from(url=git_url, to_path=dest, branch=branch)
        self._info[hs] = repo

    @staticmethod
    def _hash(git_url: str) -> str:
        """
        hash the git url as a unique key
        :param git_url: git url
        :return: md5 hash of git url
        """
        return util.md5(git_url)

    def _load(self):
        """
        load all git repo info data
        :return: None
        """
        fs = os.listdir(self._root_dir)
        for f in fs:
            fp = os.path.join(self._root_dir, f)
            if os.path.isdir(fp):
                rp = git.Repo(path=fp)
                self._info[f] = rp

    def get_info(self) -> dict:
        """
        get all the info
        :return: info
        """
        info_dict = dict()
        for hs in self._info.keys():
            repo = self._info[hs]
            try:
                info_dict[hs] = {
                    'refs': [r.remote_head for r in repo.remotes.origin.refs],
                    'tags': [t.name for t in repo.tags],
                    'branch': repo.active_branch.name,
                    'commit': {
                        'id': repo.active_branch.commit.hexsha,
                        'message': repo.active_branch.commit.message,
                        'author': repo.active_branch.commit.committer.name,
                        'time': time.strftime("%Y-%m-%d %H:%M:%S",
                                              time.gmtime(repo.active_branch.commit.committed_date))
                    },
                    'gitUrl': repo.remotes.origin.url
                }
            except Exception as e:
                LOGGER.exception('Failed to get info of repo: %s! %s' % (hs, e))
        return info_dict

    def get_commit(self, git_url: str, branch: str = 'master') -> str:
        """
        get current commit of
        :param git_url: git url
        :param branch: branch
        :return:
        """
        hs = GitRepoManager._hash(git_url)
        if hs not in self._info.keys():
            self._clone(git_url, branch)
        if hs not in self._info.keys():
            return ''
        repo = self._info[hs]
        return repo.head.commit


if __name__ == '__main__':
    manager = GitRepoManager('./tmp/git_repos')
    # print(manager.get_commit(
    #     git_url='git@github.com:utmhikari/create-skynet.git',
    #     branch='master'))

