from setuptools import setup, find_packages

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='d2r-image',
    version='0.1.1',
    description='A package for parsing items on the ground and hovered tooltips from Diablo II: Resurrected',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ezro/d2r_image",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10"
    ],
    packages=find_packages(),
    package_data={'': ['*.png']},
    include_package_data=True,
    install_requires=[
        'opencv-python',
        'keyboard',
        'pyparsing',
        'psutil',
        'mss',
        'tesserocr'
    ],
    dependency_links = [
        'https://github.com/simonflueckiger/tesserocr-windows_build/releases/download/tesserocr-v2.5.2-tesseract-4.1.1/tesserocr-2.5.2-cp39-cp39-win_amd64.whl'
    ]
)
