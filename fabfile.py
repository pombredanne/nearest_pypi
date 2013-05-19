from fabric.api import cd, env, local, run, runs_once, roles, task

env.roledefs = {
    'live': ('root@oxygen.ulo.pe', ),
}

PATHS = {
    'live': {
        'virtualenv_root': "/var/lib/virtualenvs/nearest_pypi",
        'pip': "{0[virtualenv_root]}/bin/pip",
        'python': "{0[virtualenv_root]}/bin/python",
        'project_root': "/usr/local/pythonapps/nearest_pypi",
    }
}


@task(default=True)
@roles("live")
def live(upgrade=False):
    """Deploy to the live server"""
    deploy(upgrade)


def deploy(upgrade=False):
    paths = get_paths()
    if upgrade:
        upgrade = "--upgrade"
    else:
        upgrade = ""
    with cd(paths['project_root']):
        run("git pull")
        try:
            run("supervisorctl stop nearest_pypi")
            run("{0[pip]} install {1} -r reqs/default.txt".format(paths, upgrade))
            run("{0[pip]} install {1} -r reqs/live.txt".format(paths, upgrade))
        finally:
            # make sure were running again
            run("supervisorctl start nearest_pypi")


def get_paths():
    role = next(role for role, hosts in env.roledefs.items() if env.host_string in hosts)
    return {
        k: v.format(PATHS[role]) for k, v in PATHS[role].items()
    }
