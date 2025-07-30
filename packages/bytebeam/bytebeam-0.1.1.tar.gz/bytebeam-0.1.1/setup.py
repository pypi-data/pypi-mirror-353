from setuptools import setup, find_packages

NAME = 'Dipanshu Tiwari'
EMAIL = 'dipanshutiwari115@gmail.com'

with open('README.md', 'r') as file:
    description_ = file.read()

setup(
    name='bytebeam',
    version='0.1.1',
    description='CLI File transfer tool over local network',
    author=NAME,
    author_email=EMAIL,
    maintainer=NAME,
    maintainer_email=EMAIL,
    packages=find_packages(),
    install_requires=[],

    entry_points={
        'console_scripts': [
            'bytebeam = bytebeam:main',
            'bytebeam-config = bytebeam:config',
        ],
    },

    long_description=description_,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.6',
)