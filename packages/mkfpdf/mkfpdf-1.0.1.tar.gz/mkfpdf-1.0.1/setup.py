import setuptools
from pathlib import Path

setuptools.setup(
    # 包命名
    name="mkfpdf",
    # 版本号
    version="1.0.1",
    # 添加README文件
    long_description=Path("README.md").read_text(encoding='utf-8'),
    long_description_content_type="text/markdown",
    # 排除data包
    packages=setuptools.find_packages(exclude=["data"])
)
