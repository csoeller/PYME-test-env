import condacmds as cmds

python='3.9'
environment='test-pyme-%s' % python

print("removing environment %s" % environment)
answer = input("Continue?")
if answer.lower() not in ["y","yes"]:
    print("aborting...")
    import sys
    sys.exit(1)

print("removing...")
print(cmds.conda_remove(environment))

import pathlib
build_dir = pathlib.Path("build-test")


if build_dir.exists():
    print('removing build dir "%s"' % build_dir)
    answer = input("Continue?")
    if answer.lower() not in ["y","yes"]:
        print("aborting...")
        import sys
        sys.exit(1)

    import shutil
    shutil.rmtree(build_dir)
