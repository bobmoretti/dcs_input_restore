from types import SimpleNamespace
from collections import defaultdict
from time import ctime
import os
import argparse
from glob import glob


def find_dcs_dir(openbeta):
    if openbeta:
        DCS_SAVEDGAMES_DIRNAME = 'DCS.openbeta'
    else:
        DCS_SAVEDGAMES_DIRNAME = 'DCS'

    userprofile = os.environ['USERPROFILE']
    dcs_dir = os.path.join(userprofile,
                           'Saved Games',
                           DCS_SAVEDGAMES_DIRNAME)

    return dcs_dir


def find_dcs_log(dcs_dir):
    return os.path.join(dcs_dir, 'Logs', 'dcs.log')


def get_all_device_dirs(dcs_dir):
    all_inputs = glob(dcs_dir + '/config/input/*/joystick')
    return all_inputs


def parse_dcs_log(dcs_dir):
    dev_names = []
    with open(find_dcs_log(dcs_dir), 'r') as f:
        dev_lines = []
        INPUT_LOG_STR = 'INPUT (Main): created ['

        for line in f:
            if INPUT_LOG_STR in line:
                l = line[line.find("]") + 1:]
                l = l[l.find("[") + 1: l.find("]")]
                # Avoid appending empty strings to list. All devices should be longer than 3 chars as they include UID
                if len(l) > 3:
                    dev_names.append(l)

    return set(dev_names)


def split_device_filename(filename):
    l = filename.split('{')
    guid = ''.join(l[1:]).split('}')[0]
    device_name = l[0]
    return device_name, guid


def find_dev_profiles_in(dirpath):
    def make_record(filepath):
        filename = os.path.split(filepath)[-1]
        r = SimpleNamespace()
        if filename.endswith('.diff.lua'):
            r.filename = filename
            r.device_name, r.guid = split_device_filename(filename)
            r.time = os.path.getmtime(filepath)
            return r

    filenames = glob(dirpath + '/*')
    return [make_record(filepath) for filepath in filenames
            if make_record(filepath) is not None]


def find_unique_devices(records):
    devices = defaultdict(list)
    for record in records:
        if record not in devices[record.device_name]:
            devices[record.device_name].append(record)

    def get_timestamp(rec):
        return rec.time

    for name in devices:
        devices[name].sort(key=get_timestamp)
    return devices


def update_profiles_in(dirpath, new_devs, execute=False, quiet=False):
    profiles = find_dev_profiles_in(dirpath)
    uniques = find_unique_devices(profiles)
    for dev in new_devs:
        name, guid = split_device_filename(dev)
        # does a profile with the exact same name and guid already
        # exist? if so, don't mess with it.
        already_exists = any(p.device_name == name and
                             p.guid == guid for p in profiles)
        if not already_exists:
            candidates = uniques[name]
            if len(candidates) > 0:
                # if there is at least one candidate, pick the most recent
                candidate = candidates[-1]
                old = os.path.join(dirpath, candidate.filename)
                old = os.path.normpath(os.path.abspath(old))
                new = os.path.join(dirpath, dev + '.diff.lua')
                new = os.path.normpath(os.path.abspath(new))
                if not quiet:
                    print("{}->\n{}\n".format(old, new))
                if execute:
                    os.rename(old, new)


def main(args):
    if args.dcs_dir is None:
        dcs_dir = find_dcs_dir(args.openbeta)
    if not os.path.exists(dcs_dir):
        raise ValueError("DCS directory {} does not exist".format(dcs_dir))
    if not os.path.exists(os.path.join(dcs_dir, 'Config')):
        raise ValueError("Directory {} does not seem to contain a DCS profile".format(dcs_dir))

    new_devs = parse_dcs_log(dcs_dir)
    print("*" * 80)
    print("Found the following new devices:")
    print("\n".join(new_devs))
    print("*" * 80)
    print("\n\n")
    all_profile_dirs = get_all_device_dirs(dcs_dir)
    for dirname in all_profile_dirs:
        update_profiles_in(dirname,
                           new_devs,
                           execute=args.execute,
                           quiet=args.quiet)


if __name__ == '__main__':
    desc = """Convert DCS joystick profiles from a previous install.

Useful for when you reinstall windows or move DCS to a new rig
and don't want to manually re-create all of your input profiles.

Suggested use: First run DCS on your new install. This will generate a
new dcs.log file that contains the new joystick device profile
names. Then run once with no arguments, which will print out a list of
files that will be renamed.  If you are happy with these actions, then
re-run with the -x options. If you use DCS open beta run with the -ob option"""

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--dcs_dir',
                        help='Provide path to DCS profiles directory to override default \"${USERPROFILE}/Saved Games/DCS\"')

    parser.add_argument('-ob',
                        '--openbeta',
                        help='Execute program in open beta mode (for DCS.openbeta)',
                        action='store_true')

    parser.add_argument('-x',
                        '--execute',
                        help='Execute rename. Otherwise will only do a dry-run',
                        action='store_true')

    parser.add_argument('--quiet',
                        help='Suppress output of files that are renamed',
                        action='store_true')

    args = parser.parse_args()

    main(args)
