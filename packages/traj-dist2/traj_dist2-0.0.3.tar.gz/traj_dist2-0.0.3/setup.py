import os

from setuptools import setup

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
    install_requires=["numpy>=1.16.2", "Shapely>=1.6.4", "geohash2==1.1", 'pandas>=0.20.3',
                      'scipy>=0.19.1'],
    description="Distance to compare 2D-trajectories in Pure Python",
    keywords=['trajectory', "distance", "haversine"],
    packages=["traj_dist", "traj_dist.pydist"],
    url='https://github.com/bguillouet/traj-dist',
)
