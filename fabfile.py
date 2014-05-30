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
VIRTUALENV = APP_DIR+'/venv'
SITE_SETTINGS = APP_DIR + '/site_settings.py'

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
    
    # Rename skeletons
    with cd(REPO_DJANGO_DIR):
        run('cp podcastquotes/site_settings.py.skel podcastquotes/site_settings.py')
        run('cp podcastquotes/settings.py.skel podcastquotes/settings.py')
    
    # Copy over site_settings
    run('cp {site_settings} {repo_django_dir}/podcastquotes/site_settings.py'.format(
        site_settings=SITE_SETTINGS,
        repo_django_dir=REPO_DJANGO_DIR
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
def deploy_latest():
        
        pull_repository()
        get_dependencies()
        reconfigure_app()
        migrate_database()
        test_repo()
        install_application()
        restart_server()
        