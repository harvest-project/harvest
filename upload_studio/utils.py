import subprocess


def execute_subprocess_chain(chain):
    processes = []
    p_stdin = None

    for args in chain:
        p_stdout = None if args is chain[-1] else subprocess.PIPE
        p = subprocess.Popen(args, stdin=p_stdin, stdout=p_stdout)
        processes.append(p)
        p_stdin = p.stdout

    for p in reversed(processes):
        p.communicate()

    for p in processes:
        if p.returncode != 0:
            raise Exception('Subprocess returned non-zero.')


def pprint_subprocess_chain(chain):
    return ' | '.join(' '.join(args) for args in chain)
