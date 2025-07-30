from setuptools import setup, find_packages

setup(
    name='jitsreport',
    version='0.2.1.4',
    description='A package for generating automated data profiling reports.',
    author='Surajit Das',
    author_email="mr.surajitdas@gmail.com",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where='dist_protected'),
    package_dir={'': 'dist_protected'},
    package_data={
    'jitsreport.pyarmor_runtime_000000': ['*.pyd', '*.py'],
    'jitsreport.pyarmor_runtime_000000.linux_x86_64': ['*'],
    'jitsreport.pyarmor_runtime_000000.windows_x86_64': ['*'],
    'jitsreport': ['.pyarmor.ikey'],
    },
    include_package_data=True,
    install_requires=[
        'pandas',
        'numpy',
        'plotly',
        'pdfkit',
        'openpyxl',
        'scipy',
        'matplotlib',
        'statsmodels',
        'jinja2',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
