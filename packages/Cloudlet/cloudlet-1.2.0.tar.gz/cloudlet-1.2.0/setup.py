from setuptools import setup, find_packages

setup(
    name='Cloudlet',
    version='1.2.0',
    author='Lucian',
    author_email='lucianclaudiu73@gmail.com',
    description='A Python file server with web ui with roles, based on Flask',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ByteBendr/cloudlet',
    packages=find_packages(),  # empty here unless you split code into packages
    py_modules=['cloudlet'],  # your main script without .py
    include_package_data=True,  # to include templates and static files
    install_requires=[
        'Flask>=2.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'cloudlet=cloudlet:main',  # if you add a main() function
        ],
    },
)
