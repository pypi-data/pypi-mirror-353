from setuptools import setup, find_packages

setup(
    name='camera_shield',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'opencv-python>=4.9.0',
        'numpy>=1.26.4',
        'pyyaml>=6.0.1'
    ],
    entry_points={
        'console_scripts': [
            'camera-shield=main:main'
        ]
    },
    python_requires='>=3.6',
)