"""
Module to expose more detailed version info for the installed `cydrogen`
"""
version = "0.0.5"
full_version = version
short_version = version.split('-dev')[0]
git_revision = "7735503bc3ecf494c123c8b88555cda107b5263c"
release = '-dev' not in version and '+' not in version

if not release:
    version = full_version