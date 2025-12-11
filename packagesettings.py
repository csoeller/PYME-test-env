# central package list
Packages = {
    'with_pyme_depends' : {
        # the initial matplotlib pinning should ensure we do not get a too recent version 
        'packages' : 'matplotlib<=3.6 pyme-depends'.split()
    },
    'no_pyme_depends' : {
        'packagelists_mac' : {
            'conda' : [
                ['$setuptools$'], # setuptools 74.x triggers issue https://github.com/numpy/numpy/issues/27405 on mac
                # start off with numpy/scipy
                # the "libblas=*=*accelerate" arguments according to a number of sites, e.g.
                #   - https://github.com/joblib/threadpoolctl/issues/135
                #   - https://github.com/conda-forge/numpy-feedstock/issues/303
                
                # note docs on blas selection: https://conda-forge.org/docs/maintainer/knowledge_base.html#switching-blas-implementation
                # possible options
                # conda install "libblas=*=*mkl"
                # conda install "libblas=*=*openblas"
                # conda install "libblas=*=*blis"
                # conda install "libblas=*=*accelerate"
                # conda install "libblas=*=*netlib"
                'scipy $numpy$ "libblas=*=*accelerate"'.split(),
                # next the main other dependecies
                ('$matplotlib$ pytables pyopengl jinja2 cython pip requests pyyaml' +
                 ' psutil pandas scikit-image scikit-learn sphinx toposort pybind11').split(),
                'traits traitsui pyface'.split(),
                'pyfftw zeroconf python.app'.split(),
                ['ujson'], # ujson for ClusterOfOne
                ['wxpython'],
            ],
            #'pip': ['wxpython'] # recently (Sep 24), pip installs of wx on mac seem to be broken; by contrast, conda-forge builds seem ok
            'pip': ['pymecompress'] # IO of certain h5's seems to require pymecompress; to build with recent python needs pip install
        },
        'packagelists_win' : {
            'conda': [
                ['$setuptools$'], # setuptools 74.x triggers issue https://github.com/numpy/numpy/issues/27405 on win, too!
                'scipy $numpy$'.split(), # here we should have some suitably fast installation by default but may want to check
                '$matplotlib$ pytables pyopengl jinja2 cython pip requests pyyaml'.split(),
                'psutil pandas scikit-image scikit-learn sphinx toposort pybind11'.split(),
                'traits traitsui pyface'.split(),
                'pyfftw zeroconf pywin32'.split(),
                ['pymecompress','ujson'], # IO of certain h5's seems to require pymecompress; ujson for ClusterOfOne
                # pyserial?
                ['wxpython'], # let's check if wxpython installs ok from conda-forge
            ],
            #'pip': ['wxpython']
            'pip': []
        }        
    }
}

# PYME-extra dependencies
# currently zarr<3 since zarr 3.X gives rise to an open error on zipstore zarrs;
# still need to read the migration guide if that explains things:
#       https://zarr.readthedocs.io/en/latest/user-guide/v3_migration.html
# there is an issue that mentions just this issue with v3: https://github.com/zarr-developers/zarr-python/issues/2831
#  "Can't conveniently open zip store from path with zarr v3"
#  corresponding PR with fix: https://github.com/zarr-developers/zarr-python/pull/2856
# so will hopefully be addressed in upcoming zarr 3.x update
# tabulate is not really a PYME-extra dependency but used sometimes in notebooks etc
Pymex_conda_packages = 'statsmodels roifile colorcet zarr>=2,<3 seaborn openpyxl mrcfile tabulate'.split()
# circle-fit is not available in a recent enough version via conda-forge
Pymex_pip_packages = 'circle-fit alphashape'.split()
