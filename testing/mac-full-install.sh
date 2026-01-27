python mk_pyme_env.py --python=3.11 --suffix=_t --use-git --pyme-repo=csoeller/python-microscopy --pyme-branch=recipe-macos-dpi
python add_extra_packs.py test-pyme-3.11-conda_t --pymenf pymenf-1.0.2.zip
python add_extra_packs.py test-pyme-3.11-conda_t --xtra-sets notebooks    

# tell macOS PymeApps to use this environment
defaults write org.python-microscopy.PymeApps ViewerCondaEnvironment "test-pyme-3.11-conda_t"
defaults write org.python-microscopy.PymeApps NotebookCondaEnvironment "test-pyme-3.11-conda_t"
