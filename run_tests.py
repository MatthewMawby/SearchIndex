import pytest
import os
from shutil import copyfile
from sets import Set

# root directories
SOURCE_DIR = 'src/'
TEST_DIR = 'tests/'

# service directories
UTILS_DIRECTORY = 'python/utils/'
WRITE_DIRECTORY = 'python/write/'
STOPWORD_DIRECTORY = 'python/stopword_generation/'

# package config directory
PACKAGE_CONTENTS_DIR = 'deploy/package_contents/'

# names of package_contents files for each service
WRITE_CONTENTS = ['WriteMasterNode.txt', 'WriteWorkerNode.txt']
STOPWORD_CONTENTS = ['StopWordGeneration.txt']


# copies dependencies to test directories, executes tests, removes dependencies
def main():
    copy_utils()
    copy_service(WRITE_CONTENTS, TEST_DIR + WRITE_DIRECTORY)
    copy_service(STOPWORD_CONTENTS, TEST_DIR + STOPWORD_DIRECTORY)
    pytest.main()
    remove_service(WRITE_CONTENTS, TEST_DIR + WRITE_DIRECTORY)
    remove_service(STOPWORD_CONTENTS, TEST_DIR + STOPWORD_DIRECTORY)
    remove_utils()


# reads the PACKAGE_NAMES file & determines which packages to create
def get_packages():
    packages = []
    deployments_file = open(PACKAGE_NAMES, 'r')
    for filename in deployments_file:
        packages.append(filename.strip())
    deployments_file.close()
    return packages


# gets the list of files for each package
def get_package_contents(package_name):
    package_contents = []
    contents_file = open(PACKAGE_CONTENTS_DIR + package_name, 'r')
    for filename in contents_file:
        package_contents.append(filename.strip())
    return package_contents


def copy_utils():
    for fname in os.listdir(SOURCE_DIR+UTILS_DIRECTORY):
        copyfile(SOURCE_DIR+UTILS_DIRECTORY+fname,
                 TEST_DIR+UTILS_DIRECTORY+fname)


def remove_utils():
    for fname in os.listdir(SOURCE_DIR+UTILS_DIRECTORY):
        os.remove(TEST_DIR+UTILS_DIRECTORY+fname)


def copy_service(packages, service_path):
    fpaths = Set()
    for pkg in packages:
        paths = get_package_contents(pkg)
        for p in paths:
            fpaths.add(p)
    for path in fpaths:
        fname = os.path.basename(path)
        copyfile(path, service_path + fname)


def remove_service(packages, service_path):
    fpaths = Set()
    for pkg in packages:
        paths = get_package_contents(pkg)
        for p in paths:
            fpaths.add(p)
    for path in fpaths:
        fname = os.path.basename(path)
        os.remove(service_path + fname)


if __name__ == '__main__':
    main()
