import logger
import os
import json
import git
import util
from typing import Dict, List, Any
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
        LOGGER.debug('Loaded git repos:\n%s' % util.ppf(self.get_all_info(), is_json=True))

    def _clone(self, git_url: str, ref: str = 'master', ssh_key: str = '') -> None:
        """
        :param git_url: git url
        :param ref: ref
        :param ssh_key: ssh key
        :return:
        """
        hs = GitRepoManager._hash(git_url)
        dest = os.path.join(self._root_dir, hs)
        repo = git.Repo.clone_from(url=git_url, to_path=dest, branch=ref)
        self._info[hs] = repo

    def _checkout_latest(self, git_url: str, ref: str) -> (bool, str):
        """
        checkout latest at specific ref
        :param git_url: git url
        :param ref: ref
        :return: if checkout successfully, err msg
        """
        hs = GitRepoManager._hash(git_url)
        if hs not in self._info.keys():
            self._clone(git_url, ref)
        if hs not in self._info.keys():
            return False, 'Failed to clone repo!'
        repo = self._info[hs]
        if ref in GitRepoManager._get_origin_branches(repo):
            repo.git.checkout(ref)
            repo.git.pull()
        elif ref in GitRepoManager._get_tags(repo):
            repo.git.checkout(ref)
        else:
            return False, 'Ref does not exist!'
        return True, ''

    @staticmethod
    def _get_origin_branches(repo: git.Repo) -> List[str]:
        """
        get origin branches of repo
        :param repo: git Repo Object
        :return: origin branches
        """
        return list(filter(lambda s: s != 'HEAD',
                           GitRepoManager._get_origin_refs(repo)))

    @staticmethod
    def _get_origin_refs(repo: git.Repo) -> List[str]:
        """
        get origin refs (branches + HEAD) of repo
        :param repo: git Repo Object
        :return: origin refs
        """
        return [r.remote_head for r in repo.remotes.origin.refs]

    @staticmethod
    def _get_commit_info(repo: git.Repo) -> Dict[str, Any]:
        """
        get commit info of a repo
        :param repo: git Repo Object
        :return: current commit info
        """
        return {
            'id': repo.active_branch.commit.hexsha,
            'message': repo.active_branch.commit.message,
            'author': repo.active_branch.commit.committer.name,
            'time': time.strftime("%Y-%m-%d %H:%M:%S",
                                  time.gmtime(repo.active_branch.commit.committed_date))
        }

    @staticmethod
    def _get_tags(repo: git.Repo) -> List[str]:
        """
        get tags of a repo
        :param repo: git Repo Object
        :return: tags
        """
        return [t.name for t in repo.tags]

    @staticmethod
    def _hash(git_url: str) -> str:
        """
        hash the git url as a unique key
        :param git_url: git url
        :return: md5 hash of git url
        """
        return util.md5(git_url)

    def _load(self) -> None:
        """
        load all git repo info data
        :return: None
        """
        fs = os.listdir(self._root_dir)
        for f in fs:
            fp = os.path.join(self._root_dir, f)
            if os.path.isdir(fp):
                try:
                    rp = git.Repo(path=fp)
                    self._info[f] = rp
                except Exception as e:
                    LOGGER.exception('Failed to load repo at %s! %s' % (f, e))

    def get_all_info(self) -> Dict[str, Dict[str, Any]]:
        """
        get all the info
        :return: info
        """
        info_dict = dict()
        for hs in self._info.keys():
            repo = self._info[hs]
            try:
                info_dict[hs] = {
                    'branches': GitRepoManager._get_origin_branches(repo),
                    'tags': GitRepoManager._get_tags(repo),
                    'branch': repo.active_branch.name,
                    'commit': GitRepoManager._get_commit_info(repo),
                    'gitUrl': repo.remotes.origin.url
                }
            except Exception as e:
                LOGGER.exception('Failed to get info of repo: %s! %s' % (hs, e))
        return info_dict

    def get_commit(self, git_url: str, ref: str = 'master') -> Dict[str, Any]:
        """
        get current commit of specific ref
        :param git_url: git url
        :param ref: ref
        :return: commit info
        """
        err_msg = 'Cannot get commit info of %s at ref %s!' % (git_url, ref)
        ok, msg = self._checkout_latest(git_url, ref)
        if not ok:
            LOGGER.warning(err_msg, msg)
            return dict()
        hs = GitRepoManager._hash(git_url)
        return GitRepoManager._get_commit_info(self._info[hs])

    def get_file_info(self, git_url: str, ref: str = 'master', directory: str = './') -> Dict[str, Dict[str, Any]]:
        """
        get files of a git url
        :param git_url: git url
        :param ref: ref
        :param directory: target directory
        :return: file list info
        """
        info = dict()
        err_msg = 'Cannot get file info on dir %s of %s at ref %s!' % (directory, git_url, ref)
        ok, msg = self._checkout_latest(git_url, ref)
        if not ok:
            LOGGER.warning(err_msg, msg)
            return info
        hs = GitRepoManager._hash(git_url)
        d = os.path.join(self._root_dir, hs, directory)
        if not os.path.isdir(d):
            LOGGER.warning(err_msg, 'Directory does not exist!')
            return info
        fs = os.listdir(d)
        for f in fs:
            fp = os.path.join(d, f)
            info[f] = {
                'type': 'file' if os.path.isfile(fp) else 'dir',
                'size': os.path.getsize(fp),
            }
        return info


if __name__ == '__main__':
    manager = GitRepoManager('./tmp/git_repos')
    # util.ppt(manager.get_commit(
    #     git_url='https://github.com/utmhikari/create-skynet'))
    util.ppt(manager.get_file_info(
        git_url='https://github.com/cloudwu/skynet.git'))
    util.ppt(manager.get_commit(
        git_url='https://github.com/tannerlinsley/react-table.git',
        ref='master'))
    # util.ppt(manager.get_all_info())

