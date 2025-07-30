from setuptools import setup, find_packages

setup(
    name="meshviewer",
    version="0.1.6",
    description="A modern 3D mesh viewer built with ModernGL and GLFW",
    author="Jameel Ahmed Syed",
    author_email="syedjameel9290 [at] gmail [dot] com",
    url="https://github.com/syedjameel/meshviewer",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "meshviewer": ["shaders/*.vert", "shaders/*.frag"],
    },
    install_requires=[
        "glfw>=2.9.0",
        "moderngl>=5.12.0",
        "numpy<2.0.0",
        "pyglm>=2.8.0",
        "trimesh>=3.23.0",
    ],
    entry_points={
        "console_scripts": [
            "meshviewer=meshviewer.viewer:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.9",
)