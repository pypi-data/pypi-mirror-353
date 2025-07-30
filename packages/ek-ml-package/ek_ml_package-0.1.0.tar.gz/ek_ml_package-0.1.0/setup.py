from setuptools import setup,find_packages

setup(
    name="ek_ml_package",
    version="0.1.0",
    author="Emmanuel Kirui Barkacha",
    author_email="ebarkacha@aimsammi.org",
    description="A Python package implementing fundamental machine learning algorithms from scratch with NumPy.",
    long_description=open('long_description.md').read(),
    long_description_content_type="text/markdown",
    url="https://ekbarkacha.github.io/ek_ml_package/",
    packages=find_packages(),
    install_requires=["numpy","matplotlib"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    license="MIT",
    keywords="machine learning numpy algorithms ml",
    python_requires='>=3.6',
)
