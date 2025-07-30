from setuptools import setup, find_packages

setup(
    name="douyin-live-chat",
    version="1.0.0",
    description="Douyin Live Chat Fetcher",
    long_description="A package for fetching Douyin live chat messages",
    author="bubu",
    author_email="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests>=2.31.0',
        'betterproto>=2.0.0b6',
        'websocket-client>=1.7.0',
        'mini_racer>=0.12.4'
    ],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
