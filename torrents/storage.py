import os
import shutil


def get_mount_point_of_path(path):
    while not os.path.ismount(path):
        path = os.path.dirname(path)
        if path == '/':
            break
    return path


def get_mount_point_infos_from_locations(locations):
    mount_points = set()
    for location in locations:
        mount_points.add(get_mount_point_of_path(location.pattern))
    result = []
    for mount_point in sorted(mount_points):
        usage = shutil.disk_usage(mount_point)
        result.append({
            'mount': mount_point,
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
        })
    return result
