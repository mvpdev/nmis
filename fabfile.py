import os

from fabric.api import *
from fabric.contrib import files, console
from fabric import utils
from fabric.decorators import hosts

env.home = '/home/wsgi/'
env.project = 'nmis'

sub_repositories = {
    "xform_manager": "develop", #directory: branch_to_pull
}

@hosts('wsgi@staging.mvpafrica.org')
def deploy():
    setup_env()
    for repo in sub_repositories.keys():
        pull_repo(os.path.join(env.code_root, repo), sub_repositories[repo])
    pull_repo(env.code_root, env.branch_name)
    collectstatic(env.code_root)
#    with cd(env.code_root):
#        run("pip install -r requirements.pip")

def run_in_venv(command):
    run("source %s && python manage.py collectstatic --noinput" %
                os.path.join(env.root, 'project_env', 'bin', 'activate'))

def collectstatic(repo_path):
    with cd(env.code_root):
        run_in_venv('python manage.py collectstatic --noinput')

def pull_repo(repo_path, repo_branch):
    with cd(repo_path):
        run("git pull origin %s" % repo_branch)
    
def setup_env():
    env.code_directory = 'maba_training'
    env.environment = 'staging'
    env.branch_name = 'feature/maba'
    _setup_path()

def _setup_path():
    env.root = os.path.join(env.home, 'srv', env.code_directory)
    env.code_root = os.path.join(env.root, env.project)
    env.apache_dir = os.path.join(env.root, "apache")
    env.settings = '%(project)s.settings' % env
    env.backup_dir = os.path.join(env.root, "backups")
    env.run_migration = False
