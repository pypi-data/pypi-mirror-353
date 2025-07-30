from setuptools import setup,find_packages
setup(
    name='vishnuoperators',
    version='0.2',
    packages=find_packages(),
    license='MIT',
    description='A simple Python package for basic arithmetic operations and ',
    long_description=open('README.md',encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    author='Vishnu',
    author_email='bvv@gmail.com',
    url='https://github.com/yourusername/vishnuoperators',  # optional if public
    classifiers=[],
    python_requires='>=3.6',
)