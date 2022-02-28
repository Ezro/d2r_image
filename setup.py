from setuptools import setup, find_packages


setup(
    name='d2r-image',
    version='0.0.6',
    description='A package for parsing items on the ground and hovered tooltips from Diablo II: Resurrected',
    long_description=open('README.md'),
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
        'tesserocr-2.5.2-cp39-cp39-win_amd64.whltesserocr-2.5.2.whl'
    ]
)
