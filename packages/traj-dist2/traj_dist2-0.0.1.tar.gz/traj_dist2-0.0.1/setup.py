import os

from setuptools import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

ext_modules = [Extension("traj_dist.cydist.basic_geographical", ["traj_dist/cydist/basic_geographical.pyx"],define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.basic_euclidean", ["traj_dist/cydist/basic_euclidean.pyx"],define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.sspd", ["traj_dist/cydist/sspd.pyx"],define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.dtw", ["traj_dist/cydist/dtw.pyx"],define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.lcss", ["traj_dist/cydist/lcss.pyx"],define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.hausdorff", ["traj_dist/cydist/hausdorff.pyx"],define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.discret_frechet", ["traj_dist/cydist/discret_frechet.pyx"],define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.frechet", ["traj_dist/cydist/frechet.pyx"],define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.segment_distance", ["traj_dist/cydist/segment_distance.pyx"],define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.sowd", ["traj_dist/cydist/sowd.pyx"],define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.erp", ["traj_dist/cydist/erp.pyx"],define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.edr", ["traj_dist/cydist/edr.pyx"],define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")])]

setup(
    name="traj_dist2",
    version=os.getenv("TRAJ_DIST_2_CI_VERSION", "0.0.0"),
    license="MIT",
    author="Brendan Guillouet",
    author_email="brendan.guillouet@gmail.com",
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules,
    include_dirs=[numpy.get_include()],
    install_requires=["numpy>=1.16.2", "Cython>=3", "Shapely>=1.6.4", "geohash2==1.1", 'pandas>=0.20.3',
                      'scipy>=0.19.1'],
    description="Distance to compare 2D-trajectories in Python/Cython",
    download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
    keywords = ['trajectory',"distance","haversine"],
    packages=["traj_dist", "traj_dist.cydist", "traj_dist.pydist"],
    url = 'https://github.com/bguillouet/traj-dist',
    download_urt = 'https://github.com/bguillouet/traj-dist/archive/1.1.tar.gz'
)
