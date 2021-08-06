"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    # This is the name of your project.
    name="shiroq-quantum-simulator",  # Required
    version="1.0",  # Required
    description="A simple GPU-accelerated statevector simulator",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional
    url="https://github.com/Shiro-Raven/shiroq-quantum-simulator",  # Optional
    author="Ahmed Darwish a.k.a Shiro-Raven",  # Optional
    author_email="amfa.darwish.97@gmail.com",  # Optional
    classifiers=[  # Optional
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        # Pick your license as you wish
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="quantum, simulator",  # Optional
    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    package_dir={"": "src"},  # Optional
    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=find_packages(where="src"),  # Required
    python_requires=">=3.7, <4",
    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=["numpy>=1.18", "matplotlib>=3.1"],  # Optional
    extras_require={  # Optional
        "gpu": ["cupy>=8.3"],
        "optimize": ["scipy>=1.5"],
    },
    project_urls={  # Optional
        "Bug Reports": "https://github.com/Shiro-Raven/shiroq-quantum-simulator/issues",
        "Source": "https://github.com/Shiro-Raven/shiroq-quantum-simulator/",
    },
)
