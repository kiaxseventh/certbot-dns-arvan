from setuptools import setup, find_packages

setup(
    name='certbot-dns-arvan',
    version='0.1.0',
    description='ArvanCloud DNS Authenticator plugin for Certbot',
    url='https://github.com/kiaxseventh/certbot-dns-arvan',
    author='Kiax',
    author_email='kiarash.alinejad@gmail.com',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'certbot',
        'zope.interface',
        'requests',
    ],
    entry_points={
        'certbot.plugins': [
            'dns-arvan = certbot_dns_arvan.dns_arvan:Authenticator',
        ],
    },
)