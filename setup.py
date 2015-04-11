from setuptools import setup
import yellow

setup(name='yellow-sdk-python',
      version=yellow.VERSION,
      description='Yellow Python SDK. A python module to easily integrate with the Yellow bitcoin payments API.',
      url='http://yellowpay.co',
      author='Eslam A. Hefnawy',
      author_email='eslam@yellowpay.co',
      license='MIT',
      packages=['yellow'],
      install_requires=[
        'requests==2.4.3'
      ],
      zip_safe=False)
