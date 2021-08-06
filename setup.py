from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name="shiroq-quantum-simulator",  # Required
    version="1.0",  # Required
    description="A simple GPU-accelerated statevector simulator",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional
    url="https://github.com/Shiro-Raven/shiroq-quantum-simulator",  # Optional
    author="Ahmed Darwish a.k.a Shiro-Raven",  # Optional
    author_email="amfa.darwish.97@gmail.com",  # Optional
    classifiers=[  # Optional
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="quantum, simulator",  # Optional
    package_dir={"": "src"},  # Optional
    packages=find_packages(where="src"),  # Required
    python_requires=">=3.7, <4",
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
