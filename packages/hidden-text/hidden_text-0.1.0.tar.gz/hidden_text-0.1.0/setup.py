from setuptools import setup, find_packages

setup(
    name='hidden_text',
    version='0.1.0',
    description='Cross-platform terminal password input with masked characters',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Kuldeep Singh',
    author_email='kdiitg@gmail.com',
    url='https://github.com/kdiitg/hidden_text',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Security :: Cryptography',
        'Environment :: Console'
    ],
    python_requires='>=3.6'
)
