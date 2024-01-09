from condacmds import conda_list, conda_envs, conda_create, conda_remove, repo_url

# print(conda_list('conda-builds')[-1])
# nonex = conda_list('nonexisting')
# if 'exception_name' in nonex:
#     print("exception: %s" % nonex['exception_name'])

python='3.9'
environment='test-pyme-%s' % python

envs = conda_envs()
print(envs.keys())

if environment not in envs:
    cc = conda_create(environment, python,channels=['conda-forge'])
    print(cc)

print(repo_url('PYME-extra'))

# print(conda_remove(environment))

# create new environment
# install pyme-depends
# create new subdirectory for build
# download PYME snapshot
# attempt to install (as development install?)
# test install successful
# download PYME snapshot
# attempt to install (as development install?)
# test install successful

