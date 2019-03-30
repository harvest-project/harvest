import os
import shutil


def list_rel_files(path):
    results = []
    for root, dirs, files in os.walk(path):
        for file in files:
            results.append(os.path.relpath(os.path.join(root, file), path))
    results.sort(key=lambda f: (f.count('/'), f))
    return results


def list_src_dst_files(src_path, dst_path):
    results = []
    for rel_file in list_rel_files(src_path):
        src_file = os.path.join(src_path, rel_file)
        dst_file = os.path.join(dst_path, rel_file)
        results.append((src_file, dst_file))
    return results


def copytree_into(src_path, dst_path):
    for src_file, dst_file in list_src_dst_files(src_path, dst_path):
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        shutil.copy2(src_file, dst_file)
