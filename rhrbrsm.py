#!/usr/bin/env python3
# vim: set ft=python3 ts=4 sw=4 expandtab:

import os
import re
import time

import argparse
import json
import requests
import shutil
import distutils
import hashlib
import datetime

from jinja2 import Template

__all__ = []
__author__ = "earthmeLon"
__copyright = "Copyright (C) 2022 Neo-Retro Group"
__credits__ = ["earthmeLon", "AmperSam", "flips_bad"]
__license__ = "GNU AGPLv3"
__module__ = "rhrbrsm"
__version__ = '0.1'


# ############################################################################

SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))
INSTALLSPATH = SCRIPTPATH + '/Installs'
DOWNLOADPATH = SCRIPTPATH + '/Downloads'
CONFIGSPATH = SCRIPTPATH + '/Configs'
TOOLEXTRASPATH = CONFIGSPATH + '/Tools'

RETROARCHPATH_DEFAULT = f"{SCRIPTPATH}/Emulators/RetroArch"
for path in [
    "%s/RetroArch" % (os.getenv('APPDATA', '')),
    RETROARCHPATH_DEFAULT
]:
    if os.path.exists(path):
        RETROARCHPATH_DEFAULT = path
        break
    else:
        pass

SMW_SUMS = [
    '0838e531fe22c077528febe14cb3ff7c492f1f5fa8de354192bdff7137c27f5b'
]

parser = argparse.ArgumentParser(
    description="ROMHack Races Base ROM Studio (RHRBRS) Manager",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    epilog=f"version: {__version__}",
    add_help=False
)

parser.add_argument(
    '-h', '--help', action='help', default=argparse.SUPPRESS,
    help='Show this help message and exit.'
)
versiontext = f"%(prog)s: version: {__version__}\tblame: {', '.join(__credits__)}"
parser.add_argument(
    '-v', '--version', action='version', version=versiontext,
    help='Show additional version details.'
)
parser.add_argument(
    '-t', '--target', default=__version__, type=str,
    help="Name of installation target.", dest='target'
)
parser.add_argument(
    '--install-path', default=INSTALLSPATH, type=str, nargs="?",
    help="Path for RHRBRS Installations."
)
parser.add_argument(
    '--retroarch-path', default=RETROARCHPATH_DEFAULT, type=str, nargs="?",
    help="Path to existing RetroArch emulator binary."
)
parser.add_argument(
    '--cleanrom-file', default=f"{SCRIPTPATH}/clean.smc", type=str, nargs="?",
    help="Path to Super Mario World headerless .smc ROM (ie: (U) [!]).  A copy is created in the installation directory."
)
subparsers = parser.add_subparsers(dest='action')
subparsers.required = True

parserInitialize = subparsers.add_parser('install', help="Install RHRBRS Instance")
parserInitialize.add_argument(
    '--force-download-archives', default=False,
    action='store_true',
    help="Force download of archives, even if file exists."
)
parserInitialize.add_argument(
    '--force-extract-archives', default=False,
    action='store_true',
    help="Force extraction of archives, even if directory exists."
)
parserInitialize.add_argument(
    '--force-install-configs', default=False,
    action='store_true',
    help="Force installation of tool configs.  This never happens by default, to ensure local changes aren't destroyed."
)

parserBackup = subparsers.add_parser('backup', help="Create Backup of RHRBRS Instance")
parserBackup.add_argument(
    '--backup-location', default="Backups", nargs='?',
    type=str,
    help="Path to which the backup will be saved."
)

parserBackup = subparsers.add_parser('buildbaserom', help="Build ROMHack Races BaseROM")

args = parser.parse_args()

# Note: Overwrite globals w. user provided arguments
# Note: INSTALLS vs INSTALL
BACKUPSPATH = INSTALLSPATH + '/_Backups'
INSTALLNAME = f"RHRBRS_{args.target}"
INSTALLPATH = f"{args.install_path}/{INSTALLNAME}"  # Note INSTALL vs INSTALLS
TOOLSPATH = INSTALLPATH + '/Tools'
RETROARCHPATH = args.retroarch_path

if os.path.exists(RETROARCHPATH):
    print(f"Found RetroArch: {RETROARCHPATH}")
else:
    print(f"Warning:  Unable to find RetroArch Path! {RETROARCHPATH}")

# Create HTTPS Session
session = requests.Session()
useragent = {"User-Agent": f"{__module__}/{__version__}"}
session.headers.update(useragent)


# ############################################################################


def loadConfig(configFile):
    ''' Load JSON Configuration File '''

    config = None
    try:
        with open(configFile, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Unable to load {configFile} !  {e}")
        exit(1)

    return config


def sha256checksum(file, checksums):
    ''' Return True on Valid Checksum '''

    if isinstance(checksums, (str)):
        checksums = [checksums]

    sha256buff = hashlib.sha256()
    with open(file, 'rb') as f:
        while True:
            data = f.read(65536)
            if data:
                sha256buff.update(data)
            else:
                break

    sha256sum = sha256buff.hexdigest()
    if checksums and sha256sum in checksums:
        return sha256sum
    else:
        print(f"Checksum Invalid: {file}\t{sha256sum}")
        return False


def init():
    # Create Directories
    for d in [DOWNLOADPATH, INSTALLPATH, BACKUPSPATH]:
        try:
            os.makedirs(d)
        except Exception:
            pass

    if os.path.exists(f'{INSTALLPATH}/{__module__}.json'):
        config = loadConfig(f'{INSTALLPATH}/{__module__}.json')
    else:
        config = loadConfig(f'{CONFIGSPATH}/installation.json')

    return config


def InstallTool(toolName, toolConf):
    ''' Tool Installer '''

    print(f"Installing {toolName} ".ljust(79, '-'))

    url = toolConf.get("downloadURL")
    response = requests.head(url)
    if "Content-Disposition" in response.headers.keys():
        archiveName = re.findall("filename=(.+)", response.headers["Content-Disposition"])[0]
    else:
        archiveName = os.path.basename(url)
    archiveName = archiveName.strip('\"')

    # Find or Download Tool Archive
    file = DOWNLOADPATH + '/' + archiveName
    if not os.path.exists(file) or args.force_download_archives:
        print(f"Downloading {archiveName}")
        response = requests.get(url)
        with open(file, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Found {archiveName}")
    toolConf.update({'archiveName': archiveName})

    # Verify Tool Archive Integrity
    checksum = toolConf.get('sha256sum', '')
    if sha256checksum(file, checksum):
        print(f"Checksum Valid: {archiveName}")
    else:
        print(f"Checksum Invalid: {archiveName}")
        print(f"{checksum}\tVALID_SUM")
        src = file
        dst = f"{DOWNLOADPATH}/_INVALID-{archiveName}"
        distutils.file_util.move_file(src, dst)
        print(f"Moved {src} to {dst}")
        print("Aborting!")
        exit(1)

    # Extract Archive
    extractPath = TOOLSPATH + '/' + archiveName
    for ext in ['.zip', '.tar.gz', '.7z', '.tar.xz']:
        extractPath = extractPath.removesuffix(ext)
    if not os.path.exists(extractPath) or args.force_extract_archives:
        try:
            print(f"Extracting: {archiveName}")
            shutil.unpack_archive(file, extractPath)
        except ValueError:
            print("Unsupported Archive Format: %s" % (
                '.'.join(archiveName.split('.')[1:])
            ))
    toolConf.update({'toolPath': extractPath})

    # Install Lunar Magic Plugin Libraries/Files
    lunarmagicFiles = toolConf.get('lunarmagicFiles', [])
    if lunarmagicFiles:
        print("Installing Lunar Magic Libraries")
        for fName in lunarmagicFiles:
            src = extractPath + f"/{fName}"
            dst = f"{TOOLSPATH}/lm331/"  # TODO Fix hardcode
            distutils.file_util.copy_file(src, dst)

    # Install Custom Configurations
    extrasPath = TOOLEXTRASPATH + f"/{toolName}"
    if os.path.exists(extrasPath) and args.force_install_configs:
        print("Installing Extras")
        distutils.dir_util.copy_tree(extrasPath, extractPath)

    # # Touch Null Files
    # nullFiles = toolConf.get('nullFiles', [])
    # for fName in nullFiles:
    #     distutils.file_util.write_file(
    #         f"{extractPath}/{fName}",
    #         "# File to allow committing of empty directory."
    #     )

    createDirs = toolConf.get('createDirectories', [])
    if createDirs:
        for directoryName in createDirs:
            distutils.dir_util.mkpath(f"{extractPath}/{directoryName}")

    return toolConf

# ############################################################################


def ActionUnhandledFn(action):
    print(f"Unhandled Action: {action}")


def ActionInstallTemplatesFn(toolName, toolConf, config):
    templates = toolConf.get('templates', [])
    if templates:
        toolPath = toolConf.get('toolPath')
        for t, dst in templates.items():
            print(f"Rendering {toolPath}/{dst}")
            with open(f"{CONFIGSPATH}/Templates/{t}", 'r') as f:
                template = Template(f.read())
            with open(f"{toolPath}/{dst}", 'w') as f:
                f.write(template.render(config=config))


def ActionInstallFn():
    print("Running Installation ".ljust(79, '#'))

    config = loadConfig(f'{CONFIGSPATH}/installation.json')
    tools = config.get("tools")

    installedTools = {}
    # Prioritize Lunar Magic
    installedTools.update({
        'lunarmagic': InstallTool('lunarmagic', tools.pop('lunarmagic'))
    })
    # Install Tools
    for toolName, toolConf in tools.items():
        updates = InstallTool(toolName, toolConf)

        # Update Installation State
        toolConf.update(updates)
        installedTools.update({toolName: toolConf})

    # Update Configuration
    config.update({
        'rhrbrsm': {'version': __version__},
        'installPath': INSTALLPATH,
        'installName': INSTALLNAME,
        'tools': installedTools,
        'retroarchPath': RETROARCHPATH
    })
    tools = config.get("tools")

    # Write out configuration used
    with open(INSTALLPATH + '/rhrbrsm.json', 'w') as f:
        f.write(json.dumps(config, indent=2, sort_keys=True))

    # Render and Install Templates
    for toolName, toolConf in tools.items():
        ActionInstallTemplatesFn(toolName, toolConf, config)

    # Copy over cleanrom
    cleanromFile = args.cleanrom_file
    if os.path.exists(cleanromFile):
        if sha256checksum(cleanromFile, SMW_SUMS):
            print(f"Found SMW ROM: {cleanromFile}")
        else:
            print(f"Warning:  Found unclean/odd SMW ROM: {cleanromFile} ".ljust(79, '<'))
    else:
        print(f"Warning:  Unable to find clean SMW ROM! {cleanromFile} ".ljust(79, '<'))

    distutils.file_util.copy_file(
        args.cleanrom_file, f"{INSTALLPATH}/clean.smc"
    )


def ActionBackupFn(config):
    print("Running Backup ".ljust(79, '-'))

    installPath = config.get("installPath", INSTALLPATH)
    installName = config.get("installName", INSTALLNAME)

    today = datetime.date.today()
    timehack = "%s-%s" % (today.year, today.timetuple().tm_yday)
    timehack_specific = "%s-%s" % (timehack, str(time.time_ns())[:12])
    backupPaths = (
        f"{BACKUPSPATH}/{installName}-{timehack}",
        f"{BACKUPSPATH}/{installName}-{timehack_specific}"
    )

    isBackedUp = False
    for backupPath in backupPaths:
        if not os.path.exists(backupPath):
            print(f"Backing up {installName}: {backupPath}")
            distutils.dir_util.copy_tree(installPath, backupPath)
            isBackedUp = True
            break
        else:
            continue

    if isBackedUp:
        print("Backup successful 👍".ljust(79, ' '))
    else:
        print("Backup failed 👎".ljust(79, '<'))
        exit(1)


def ActionBuildBaseROM(config):
    rhrbr_version = config.get('rhrbr').get('version')
    print(f"Build RHR BaseROM ({rhrbr_version}) ".ljust(79, '-'))

    print("TODO!")


# ############################################################################


if __name__ == '__main__':
    action = args.action

    config = init()

    match action:
        case "install":
            ActionInstallFn()
        case "backup":
            ActionBackupFn(config)
        case "buildbaserom":
            ActionBuildBaseROM(config)
        case _:
            ActionUnhandledFn(action)

# ############################################################################
