from setuptools import setup, find_packages
import sys

# 系统要求检查
if sys.platform != 'win32':
    raise RuntimeError("This package requires Windows 10 or later")

setup(
    name="douyin-live-fetcher",
    version="1.0.0",
    author="Original Author",
    description="Douyin Live Web Fetcher",
    long_description=open("README.MD", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests==2.31.0",
        "betterproto==2.0.0b6", 
        "websocket-client==1.7.0",
        "PyExecJS==1.5.1",
        "mini_racer==0.12.4"
    ],
    entry_points={
        'console_scripts': [
            'douyin-fetcher=DouyinLiveWebFetcher.main:run',
        ],
    },
    include_package_data=True,
    package_data={
        'DouyinLiveWebFetcher': ['*.js', 'protobuf/*', '*.jpg']
    },
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
    ]
)
