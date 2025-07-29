import os
import subprocess
from functools import partial

import pytest


@pytest.fixture(scope="session")
def vcs_username():
    return "Your Name"


@pytest.fixture(scope="session")
def vcs_email():
    return "mail@localhost"


@pytest.fixture(scope="session")
def subprocess_env(vcs_email, vcs_username):
    with pytest.MonkeyPatch.context() as context:
        context.setenv("GIT_AUTHOR_NAME", vcs_username)
        context.setenv("GIT_AUTHOR_EMAIL", vcs_email)
        context.setenv("GIT_COMMITTER_NAME", vcs_username)
        context.setenv("GIT_COMMITTER_EMAIL", vcs_email)
        env = os.environ.copy()
        env["HGENCODING"] = "utf-8"
        yield env


@pytest.fixture(scope="session")
def call(subprocess_env):
    return partial(subprocess.call, env=subprocess_env, shell=True)


@pytest.fixture(scope="session")
def check_call(subprocess_env):
    return partial(subprocess.check_call, env=subprocess_env)


@pytest.fixture(scope="session")
def check_output(subprocess_env):
    return partial(subprocess.check_output, env=subprocess_env)


@pytest.fixture(scope="session")
def run(subprocess_env):
    return partial(subprocess.run, env=subprocess_env)


class VCS:
    GIT = "git"
    MERCURIAL = "hg"


@pytest.fixture(scope="session")
def check_vcs_presence(call):
    def checker(vcs: str) -> str:
        if call(f"{vcs} version") != 0:
            pytest.xfail(reason=f"{vcs} is not installed.")
        return vcs
    return checker


@pytest.fixture(scope="session", params=[VCS.GIT, VCS.MERCURIAL])
def vcs(request, check_vcs_presence):
    """Return all supported VCS systems (git, hg)."""
    return check_vcs_presence(vcs=request.param)


@pytest.fixture(scope="session")
def git(check_vcs_presence):
    """Return git as VCS (not hg)."""
    return check_vcs_presence(vcs=VCS.GIT)
