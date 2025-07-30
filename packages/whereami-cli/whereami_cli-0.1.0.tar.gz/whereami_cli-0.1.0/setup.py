from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="whereami-cli",
    version="0.1.0",
    author="ZhangZimin",
    author_email="641945043@qq.com",
    description="用于获取当前用户的经纬度位置信息的命令行工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zhangzimin/geo-location",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "geocoder>=1.38.1",
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "whereami=get_location:get_current_location",
        ],
    },
) 