#!/usr/bin/env python

from __future__ import print_function
import pprint, sys, os

# print("%s" % sys.argv)
STACKNAME = sys.argv[1]
outfile = sys.argv[3]
out = open(outfile, "w")
#print("Interrogating setup.py for package %s into %s " % (STACKNAME, outfile),
#      file=sys.stderr)

def mysetup(*args, **kwargs):
    global out
    if 'version' not in kwargs:
        print("""
    *** Unable to find 'version' in setup.py of %s
""" % STACKNAME)
        raise RuntimeError("version not found in setup.py")

    print(r'set(%s_VERSION "%s")' % (STACKNAME, kwargs['version']), file=out)
    print(r'set(%s_SCRIPTS "%s")' % (STACKNAME,
                                     ';'.join(kwargs.get('scripts', []))), file=out)

    if 'package_dir' not in kwargs:
        raise RuntimeError(r'package_dir not in setup.py', file=sys.stderr)

    package_dir = kwargs['package_dir']
    allprefix=package_dir.get('', None)

    pkgs = kwargs.get('packages', [])

    # Remove packages with '.' separators.  setuptools requires
    # specifying submodules.  The symlink approach of catkin does not
    # work with submodules.  In the common case, this does not matter
    # as the submodule is within the containing module.  We verify
    # this assumption, and if it passes, we remove submodule packages.
    for pkg in pkgs:
        splits = pkg.split('.')
        # hack: ignore write-combining setup.py files for msg and srv
        # files
        if len(splits) > 1 and splits[1] not in ['msg', 'srv']: 
            top_level = splits[0]
            top_level_dir = package_dir[top_level]
            expected_dir = os.path.join(top_level_dir, os.path.join(*splits[1:]))
            actual_dir = package_dir[pkg]
            if not os.path.samefile(expected_dir, actual_dir):
                raise RuntimeError("catkin_export_python does not support setup.py files that combine across multiple directories")

    # If checks pass, remove all submodules
    pkgs = [p for p in pkgs if '.' not in p]

    resolved_pkgs = []
    for pkg in pkgs:
        if allprefix:
            resolved_pkgs += [os.path.join(allprefix, pkg)]
        else:
            resolved_pkgs += [package_dir[pkg]]

    print(r'set(%s_PACKAGES "%s")' % (STACKNAME, ';'.join(pkgs)), file=out)
    print(r'set(%s_PACKAGE_DIRS "%s")' % (STACKNAME, ';'.join(resolved_pkgs).replace("\\","/")), file=out)

class Dummy: pass

d = Dummy()
setattr(d, 'setup', mysetup)

sys.modules['setuptools'] = d
sys.modules['distutils.core'] = d

# print("execcing %s" % sys.argv[2])

# be sure you're in the directory containing
# setup.py so the sys.path manipulation works,
# so the import of __version__ works
os.chdir(os.path.dirname(os.path.abspath(sys.argv[2])))

execfile(sys.argv[2])






