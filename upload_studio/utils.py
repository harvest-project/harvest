import os
import shutil
import subprocess


def list_abs_files(path):
    results = []
    for root, dirs, files in os.walk(path):
        for file in files:
            results.append(os.path.join(root, file))
    results.sort(key=lambda f: (f.count('/'), f))
    return results


def list_rel_files(path):
    return [os.path.relpath(f, path) for f in list_abs_files(path)]


def list_src_dst_files(src_path, dst_path):
    return [
        (os.path.join(src_path, rel_file), os.path.join(dst_path, rel_file))
        for rel_file in list_rel_files(src_path)
    ]


def copytree_into(src_path, dst_path):
    for src_file, dst_file in list_src_dst_files(src_path, dst_path):
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        shutil.copy2(src_file, dst_file)


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


def strip_invalid_path_characters(path):
    return ''.join(c for c in path if c not in r'\/:*?"<>|')
