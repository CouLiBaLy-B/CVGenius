from setuptools import setup, find_packages

setup(
    name='CVGenius',
    version='0.1.0',
    description='A comprehensive CV management application',
    author='Ibrahim COULIBALY',
    author_email='icoulbi4@gmail.com',
    url='https://github.com/coulibaly-b/CVGenius',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=[
        'pytest',
        'pyyaml',
        # Add other dependencies here
    ],
    extras_require={
        'dev': [
            'pytest-cov',
            'flake8',
            'black',
            # Add other development dependencies here
        ],
    },
    entry_points={
        'console_scripts': [
            # If you have any scripts to run
            # 'script_name = module:function',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',  # Adjust as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # Adjust if different
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.7',
)
