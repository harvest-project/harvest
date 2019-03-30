import os
import shutil


def copytree_into(src_path, dst_path):
    for root, dirs, files in os.walk(src_path):
        root_relative = os.path.relpath(src_path)
        root_dst = os.path.join(dst_path, root_relative)
        os.makedirs(root_dst, exist_ok=True)
        for file in files:
            src = os.path.join(root, file)
            file_relative = os.path.join(root_relative, file)
            dst = os.path.join(dst_path, file_relative)
            shutil.copy2(src, dst)
