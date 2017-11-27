This directory specifies which packages should be created as well
as the contents for each package.


To configure a new package, add a new 'PACKAGE_NAME.txt' file to
'deployment_packages.txt' replacing PACKAGE_NAME with the name of
the package you wish to create.

Next add a corresponding 'PACKAGE_NAME.txt' file to the 'package_contents'
directory. This file should contain newline separated paths to
each file that should be included in that package. The path should
be a relative path from the root directory of the project (e.g 'src/python...').


After creating the configuration, deployments can be created or
updated by running 'python create_deployment_packages.py' from
the project root directory.
