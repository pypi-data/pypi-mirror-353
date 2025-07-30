from setuptools import setup, find_packages

setup(
    name="PY_TELUGU_VERSION",
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pythontel = PY_TELUGU_VERSION.auto_update:main',
            'pythonrun = PY_TELUGU_VERSION.main:main',
        ],
    },
    author="sunstromium",
    description="literal telugu package for python programming",
    long_description="-- — test version",
    long_description_content_type="text/plain",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
