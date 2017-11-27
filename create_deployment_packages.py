import zipfile
import os

PACKAGE_NAMES = 'deploy/deployment_packages.txt'
PACKAGE_CONTENTS_DIR = 'deploy/package_contents/'
DEPLOYMENT_DIRECTORY = 'deploy/packages/'


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


# creates a zip for each package, zips are saved to DEPLOYMENT_DIRECTORY
def create_deployment(package_name, package_contents):
    if not os.path.exists(DEPLOYMENT_DIRECTORY):
        os.makedirs(DEPLOYMENT_DIRECTORY)
    package_name = os.path.splitext(package_name)[0]
    deployment_name = DEPLOYMENT_DIRECTORY + package_name + '.zip'
    with zipfile.ZipFile(deployment_name, 'w') as deployment:
        for item in package_contents:
            deployment.write(item, os.path.basename(item))
        deployment.close()


def main():
    # determine which packages to create
    packages = get_packages()

    # get the files for each deployment & create a zip
    for package in packages:
        files_in_package = get_package_contents(package)
        create_deployment(package, files_in_package)


if __name__ == '__main__':
    main()
