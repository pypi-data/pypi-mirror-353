"""
Module to expose more detailed version info for the installed `cydrogen`
"""
version = "0.0.6"
full_version = version
short_version = version.split('-dev')[0]
git_revision = "f28dd47b0477f8566fe1bd4f5f5399ec66f92c40"
release = '-dev' not in version and '+' not in version

if not release:
    version = full_version