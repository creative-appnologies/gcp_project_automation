from setuptools import setup

setup(
    name='GCPProjectAutomation',
    version=0.1,
    author='James Hinton',
    author_email='info@creativeappnologies.com',
    packages=['gcpprojectautomation',
              'tests'],
    scripts=[],
    url='',
    license='LICENSE',
    description='Package to simplify aspects of project creation on Google Cloud',
    long_description=open('README.md').read(),
    install_requires=["google-api-python-client", "google-auth"],
    package_data={

    },
)
