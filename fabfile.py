import os

from fabric.api import *
from fabric.contrib import files, console
from fabric import utils
from fabric.decorators import hosts

from datetime import datetime

DEFAULT_SETTINGS = {
    'deployments_path': '/home/wsgi/srv',
    'host': 'wsgi@staging.mvpafrica.org',
    'project_name': 'nmis',
    'virtualenv_directory': 'project_env',
    'backup': True,
    'migrate': True,
    }

DEPLOYMENTS = {
    'staging': {
        'folder_name': 'nmis-staging',
        'branch': 'develop',
        'backup': False,
        },
    'production': {
        'folder_name': 'nmis-production',
        'branch': 'master',
        'database_name': 'nmispilot_phaseII',
        },
    }


@hosts(DEFAULT_SETTINGS['host'])
def deploy(deployment_name):
    """
    fab deploy:staging

    1. Back up database.
    2. Pull updated code.
    3. Activate virtualenv.
    4. Install pip requirements.
    5. Migrate database.
    6. Reparse surveys.
    7. Restart server.
    """
    deployment = DEFAULT_SETTINGS.copy()
    deployment.update(DEPLOYMENTS[deployment_name])
    deployment['project_path'] = os.path.join(
        deployment['deployments_path'],
        deployment['folder_name']
        )
    deployment['code_path'] = os.path.join(
        deployment['project_path'],
        'nmis'
        )
    deployment['apache_dir'] = os.path.join(
        deployment['project_path'],
        'apache'
        )


    def backup_database():
        cur_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_directory_path = os.path.join(
            COMMON_SETTINGS['deployments_path'],
            'backups',
            cur_timestamp
            )
        tarball_path = os.path.join(backup_directory_path, deployment['project_name'])
        run("mkdir -p %s" % backup_directory_path)
        with cd(backup_directory_path):
            run("mysqldump -u nmis -p$MYSQL_NMIS_PW %(database_name)s > %(database_name)s.sql" % deployment)
            run("gzip %(database_name)s.sql" % deployment)

    def pull_code():
        """
        Pulls updated code from nmis and xform_manager repos.
        """
        sub_repositories = ["xform_manager"]
        sub_repo_paths = [os.path.join(deployment['code_path'], repo) for repo in sub_repositories]
        with cd(deployment['code_path']):
            run("git pull origin %(branch)s" % deployment)

        for repo_path in sub_repo_paths:
            with cd(repo_path):
                run("git pull origin %(branch)s" % deployment)

    def _run_in_virtualenv(command):
        activate_path = os.path.join(
            deployment['project_path'],
            deployment['virtualenv_directory'],
            'bin', 'activate'
            )
        activate_virtualenv = "source %s" % activate_path
        run(activate_virtualenv + ' && ' + command)

    def install_pip_requirements():
        """
        deleting django-eav from the virtualenv in order to force a
        new download and avoid a pip error.
        """
        with cd(deployment['code_path']):
            _run_in_virtualenv("pip install -r requirements.txt")

    def migrate_database():
        if deployment['migrate']:
            with cd(deployment['code_path']):
                _run_in_virtualenv("python manage.py migrate")

    def reparse_surveys():
        with cd(deployment['code_path']):
            _run_in_virtualenv("python manage.py reparse")

    def restart_web_server():
        """
        touch wsgi file to trigger reload
        """
        with cd(deployment['apache_dir']):
            run("touch environment.wsgi")

    if deployment['backup']:
        backup_database()
    pull_code()
    install_pip_requirements()
    migrate_database()
    # reparse_surveys()
    restart_web_server()
