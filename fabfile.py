import os
from fabric.api import env, cd, run
from datetime import datetime

# default settings for all deployments
env.update(
    {
        'deployments_path': '/home/wsgi/srv',
        'hosts': ['wsgi@staging.mvpafrica.org'],
        'project_name': 'nmis',
        'virtualenv_directory': 'project_env',
        'migrate': True,
        }
    )

DEPLOYMENTS = {
    'staging': {
        'folder_name': 'nmis-staging',
        'branch': 'develop',
        'backup': False,
        },
    'production': {
        'folder_name': 'nmis-production',
        'branch': 'master',
        'backup': True,
        'database_name': 'nmispilot_phaseII',  # todo: remove hard code
        },
    }


def _setup_env(deployment_name):
    env.update(DEPLOYMENTS[deployment_name])
    env.project_path = os.path.join(
        env.deployments_path,
        env.folder_name
        )
    env.code_path = os.path.join(
        env.project_path,
        'nmis'
        )
    env.apache_dir = os.path.join(
        env.project_path,
        'apache'
        )


def backup(deployment_name):
    _setup_env(deployment_name)
    cur_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    env.backup_directory_path = os.path.join(
        env.project_path,
        'backups',
        cur_timestamp
        )
    run("mkdir -p %(backup_directory_path)s" % env)
    with cd(env.backup_directory_path):
        run("mysqldump -u nmis -p$MYSQL_NMIS_PW %(database_name)s > %(database_name)s.sql" % env)
        run("gzip %(database_name)s.sql" % env)


def deploy(deployment_name, reparse="all"):
    """
    Example command line usage:
    fab deploy:staging,reparse=none
    """
    _setup_env(deployment_name)

    if env.backup:
        backup(deployment_name)

    def pull_code():
        """
        Pull updated code from nmis repo.
        """
        with cd(env.code_path):
            run("git pull origin %(branch)s" % env)
    pull_code()

    def _run_in_virtualenv(command):
        activate_path = os.path.join(
            env.project_path,
            env.virtualenv_directory,
            'bin', 'activate'
            )
        activate_virtualenv = "source %s" % activate_path
        run(activate_virtualenv + ' && ' + command)

    def install_pip_requirements():
        """
        deleting django-eav from the virtualenv in order to force a
        new download and avoid a pip error.
        """
        with cd(env.code_path):
            _run_in_virtualenv("pip install -r requirements.txt")
    install_pip_requirements()

    def migrate_database():
        if env.migrate:
            with cd(env.code_path):
                _run_in_virtualenv("python manage.py migrate")
    migrate_database()

    def reparse_surveys():
        with cd(env.code_path):
            _run_in_virtualenv("python manage.py reparse")
    if reparse == "all":
        reparse_surveys()

    def restart_web_server():
        """
        touch wsgi file to trigger reload
        """
        with cd(env.apache_dir):
            run("touch environment.wsgi")
    restart_web_server()
