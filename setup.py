from setuptools import find_packages, setup

setup_args = dict(
    name='meta.data',
    use_scm_version=True,
    namespace_packages=['meta'],
    packages=find_packages(),
    include_package_data=True,
    author='Darwin Monroy',
    author_email='contact@darwinmonroy.com',
    url='https://github.com/dmonroy/meta.data',
    license='MIT License',
    description='Stores data about data',
    setup_requires=[
        'setuptools_scm',
    ],
    install_requires=[
        'aiopg',
        'attrdict',
        'chilero',
        'pyyaml',
        'schema_migrations',
    ],
    entry_points = {
        'console_scripts': [
            'meta.data = meta.data:main',
        ],
    },
)


if __name__ == '__main__':
    setup(**setup_args)