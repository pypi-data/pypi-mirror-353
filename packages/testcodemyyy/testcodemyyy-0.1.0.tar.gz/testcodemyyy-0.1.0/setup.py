from setuptools import setup, find_packages

setup(
    name='testcodemyyy',
    version='0.1.0',
    author='MohammadReza',
    author_email='narnama.room@gmail.com',
    description='A cool Python library with awesome features 🐍✨',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    python_requires='>=3.6',
    include_package_data=True,
)
