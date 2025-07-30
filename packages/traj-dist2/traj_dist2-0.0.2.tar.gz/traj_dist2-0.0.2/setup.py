import os

from setuptools import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

# Using Cython3 and define_macros to avoid numpy warning at compile time
# https://docs.cython.org/en/latest/src/userguide/numpy_tutorial.html#compilation-using-setuptools
ext_modules = [Extension("traj_dist.cydist.basic_geographical", ["traj_dist/cydist/basic_geographical.pyx"],
                         define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.basic_euclidean", ["traj_dist/cydist/basic_euclidean.pyx"],
                         define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.sspd", ["traj_dist/cydist/sspd.pyx"],
                         define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.dtw", ["traj_dist/cydist/dtw.pyx"],
                         define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.lcss", ["traj_dist/cydist/lcss.pyx"],
                         define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.hausdorff", ["traj_dist/cydist/hausdorff.pyx"],
                         define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.discret_frechet", ["traj_dist/cydist/discret_frechet.pyx"],
                         define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.frechet", ["traj_dist/cydist/frechet.pyx"],
                         define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.segment_distance", ["traj_dist/cydist/segment_distance.pyx"],
                         define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.sowd", ["traj_dist/cydist/sowd.pyx"],
                         define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.erp", ["traj_dist/cydist/erp.pyx"],
                         define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]),
               Extension("traj_dist.cydist.edr", ["traj_dist/cydist/edr.pyx"],
                         define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")])]

def version():
    ref = os.getenv("GITHUB_REF","")
    if ref and ref.startswith("refs/tags"):
        # tag
        return ref.split("/")[-1]
    elif ref:
        # normal branch commit
        return f'0.0.0+{ref.split("/")[-1]}.{os.getenv("GITHUB_SHA")[:7]}'
    else:
        # local dev
        return "0.0.0"

setup(
    name="traj_dist2",
    version=version(),
    license="MIT",
    author="Brendan Guillouet",
    author_email="brendan.guillouet@gmail.com",
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules,
    include_dirs=[numpy.get_include()],
    install_requires=["numpy>=1.16.2", "Cython>=3", "Shapely>=1.6.4", "geohash2==1.1", 'pandas>=0.20.3',
                      'scipy>=0.19.1'],
    description="Distance to compare 2D-trajectories in Python/Cython",
    keywords=['trajectory', "distance", "haversine"],
    packages=["traj_dist", "traj_dist.cydist", "traj_dist.pydist"],
    url='https://github.com/bguillouet/traj-dist',
)
