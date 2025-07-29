from setuptools import setup

setup(
      name='mockoauthserver',

      version='4.7',
      description='Library for _uois project.',
      url='https://github.com/hrbolek/PyMockOAuthServer',
      author='Profesor Hrbolek',
      author_email='profesor@hrbolek.cz',
      license='MIT',
      packages=['mockoauthserver'],
      install_requires=[
          'fastapi',
          'python-multipart',
          'pyjwt[crypto]',
          'cryptography'
      ],      
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Database',
      ],
      zip_safe=False)
