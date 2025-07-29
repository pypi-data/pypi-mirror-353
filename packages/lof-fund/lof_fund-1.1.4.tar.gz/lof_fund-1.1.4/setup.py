from setuptools import setup

setup(
    name="lof-fund",
    version="1.1.4",
    author="Egg*4",
    author_email="1127885315@qq.com",  # 替换为你的邮箱
    description="获取基金溢价率的脚本",
    long_description=open("./README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    py_modules=["lof"],
    install_requires=[
        "chinesecalendar",
        "schedule",
        "requests",
        "pandas",
        "akshare",
        "beautifulsoup4",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "lofpm=lof:main"
        ]
    },
)
