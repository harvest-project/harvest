import subprocess


def execute_subprocess_chain(chain_args):
    processes = []
    p_stdin = None

    for options in chain_args:
        p_stdout = None if options is chain_args[-1] else subprocess.PIPE
        p = subprocess.Popen(options, stdin=p_stdin, stdout=p_stdout)
        processes.append(p)
        p_stdin = p.stdout

    for p in reversed(processes):
        p.communicate()

    for p in processes:
        if p.returncode != 0:
            raise Exception('Subprocess returned non-zero.')
