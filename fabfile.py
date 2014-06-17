"""
Deploy script for WebFaction hosting.

To deploy latest code:
> fab -H hostname_of_webfaction deploy_latest
"""

from fabric.api import task, run, env
from fabric.context_managers import cd
from fabtools.python import virtualenv
from fabtools import require

env.use_ssh_config = True



# SERVER VALUES

REPO_DIR = '/home/oceancron/git/podcastquotes'
REPO_DJANGO_DIR = REPO_DIR + '/django_project'

APP_DIR = '/home/oceancron/webapps/podcastquotes'
DJANGO_PROJECT = APP_DIR+'/django_project'
VIRTUALENV = '/home/oceancron/python-virtualenvs/podverse'
SITE_SETTINGS = APP_DIR + '/site_settings.py'
SECRETS_CFG = APP_DIR + '/secrets.cfg'

if None in [REPO_DIR, APP_DIR, DJANGO_PROJECT, VIRTUALENV, 
    SITE_SETTINGS]:
        print("Fabfile not configured with server values. Exiting")
        exit()

@task
def pull_repository():
    
    with cd(REPO_DIR):
        
        # Get fresh copy of repo
        run("git reset --hard HEAD")
        run("git pull")

@task
def get_dependencies():
    
    with virtualenv(VIRTUALENV):
    
        install_deps_cmd = "pip install -r {repo_dir}/requirements.txt"
        run(install_deps_cmd.format(
            repo_dir=REPO_DIR
        ))
        
        require.python.package('psycopg2')

@task
def test_repo():
    
    with virtualenv(VIRTUALENV):
        with cd(REPO_DJANGO_DIR):
            run('./manage.py test')

@task
def reconfigure_app():
    
    # Rename setting skeleton
    with cd(REPO_DJANGO_DIR):
        run('cp podcastquotes/settings.py.skel podcastquotes/settings.py')
    
    # Link over site_settings
    with cd(REPO_DJANGO_DIR + '/podcastquotes'):
        run('rm site_settings.py')
        run('ln -s {site_settings}'.format(
            site_settings=SITE_SETTINGS
        ))
    
    # Link over site secrets config
    with cd(REPO_DJANGO_DIR):
        run('rm secrets.cfg')
        run('ln -s {secrets_cfg}'.format(
            secrets_cfg=SECRETS_CFG
        ))

@task
def migrate_database():

    with virtualenv(VIRTUALENV):
        with cd(REPO_DJANGO_DIR):
            run('./manage.py syncdb')
            run('./manage.py migrate')

@task
def collect_static_files():
    
    with virtualenv(VIRTUALENV):
        with cd(DJANGO_PROJECT):
            run('./manage.py collectstatic --noinput')

@task
def install_application():
    
    # Backup previous install
    run('mv {DJANGO_PROJECT} {DJANGO_PROJECT}_`date +%s`'.format(
        DJANGO_PROJECT = DJANGO_PROJECT,
    ))
    
    # Move repo files over to deploy django_project directory
    run('cp -ar {REPO_DIR}/django_project {DJANGO_PROJECT}'.format(
        REPO_DIR=REPO_DIR,
        DJANGO_PROJECT=DJANGO_PROJECT
    ))
    
    collect_static_files()

@task
def restart_server():
    run(APP_DIR+'/apache2/bin/restart')
    
@task
def deployment_tests():
    with virtualenv(VIRTUALENV):
        with cd(DJANGO_PROJECT):
            run('./manage.py deploy_tests')

@task
def install_cronjobs():
    
    install_cron = '{REPO_DIR}/install_cron.sh'.format(
        REPO_DIR=REPO_DIR)
    
    run('{install_cron} {django_project} {virtualenv}'.format(
        install_cron=install_cron,
        django_project=DJANGO_PROJECT,
        virtualenv=VIRTUALENV
    ))

@task
def deploy_latest():
    
    pull_repository()
    get_dependencies()
    reconfigure_app()
    migrate_database()
    test_repo()
    install_application()
    install_cronjobs()
    deployment_tests()
    restart_server()
    
