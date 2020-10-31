import subprocess


def get_flac_version():
    return subprocess.check_output(['flac', '--version']).decode().split('\n')[0]


def get_lame_version():
    return subprocess.check_output(['lame', '--version']).decode().split('\n')[0]
