from setuptools import setup, find_packages

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='d2r-image',
    version='0.1.16',
    description='D2R Image is a package aimed to help in providing an API for answering common questions when looking at a Diablo II: Resurrected image',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ezro/d2r_image",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10"
    ],
    packages=find_packages(exclude=['tests*']),
    package_data={'': ['*.png']},
    include_package_data=True,
    install_requires=[
        'opencv-python',
        'keyboard',
        'pyparsing',
        'psutil',
        'mss',
        'tesserocr',
        'dataclasses-json',
        'parse',
    ],
    dependency_links = [
        'https://github.com/simonflueckiger/tesserocr-windows_build/releases/download/tesserocr-v2.5.2-tesseract-4.1.1/tesserocr-2.5.2-cp39-cp39-win_amd64.whl'
    ]
)
