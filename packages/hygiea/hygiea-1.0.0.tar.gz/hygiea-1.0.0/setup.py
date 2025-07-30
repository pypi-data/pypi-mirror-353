"""Setup script for Hygiea package."""

from setuptools import setup, find_packages

# Read version
version = {}
with open("hygiea/__version__.py") as fp:
    exec(fp.read(), version)

# Read README for long description
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "A comprehensive Python toolkit for data cleaning and preprocessing"

# Read requirements
try:
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
except FileNotFoundError:
    requirements = [
        'pandas>=1.3.0',
        'numpy>=1.21.0',
        'scikit-learn>=1.0.0',
        'scipy>=1.7.0',
        'matplotlib>=3.5.0',
        'seaborn>=0.11.0'
    ]

setup(
    name='hygiea',
    version=version['__version__'],
    author='Hygiea Development Team',
    author_email='hygiea@example.com',
    description='A comprehensive Python toolkit for data cleaning and preprocessing',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/hygiea',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'isort>=5.0',
        ],
        'full': [
            'plotly>=5.0',
            'statsmodels>=0.13.0',
            'sqlalchemy>=1.4.0',
        ],
    },
    keywords='data-cleaning preprocessing pandas machine-learning eda',
)
