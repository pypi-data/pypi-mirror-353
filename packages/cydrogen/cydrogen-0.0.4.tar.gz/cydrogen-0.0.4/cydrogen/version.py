
"""
Module to expose more detailed version info for the installed `cydrogen`
"""
version = "0.0.4"
full_version = version
short_version = version.split('.dev')[0]
git_revision = "ee4f514aeebebb60139101c08cd4432b0b707007"
release = 'dev' not in version and '+' not in version

if not release:
    version = full_version
