# Python 包发布简明流程指南
## 1. 准备发布环境
```
# 安装必要工具
pip install -U setuptools wheel twine
```
## 2. 创建项目目录结构
```
# 创建项目目录
mkdir mypackage
# 进入目录
cd mypackage
# 创建标准目录结构
mkdir -p mypackage data tests
touch mypackage/__init__.py
touch mypackage/main.py
touch setup.py
touch README.md
touch LICENSE
# 打开vscode
code .   
```
**标准目录结构**
```
mypackage/
├── data/                   # 数据文件目录
├── mypackage/              # 主代码包
│   ├── __init__.py         # 包初始化文件
│   └── main.py             # 主代码文件
├── setup.py                # 包配置
├── LICENSE                 # 许可证文件
└── README.md               # 项目文档
```
## 3. 创建核心文件
```
1. setup.py 配置
2. LICENSE 文件
3. README.md 
```
## 4. 构建分发包
```
# 1. 清理旧文件
Remove-Item -Recurse -Force build, dist, *.egg-info -ErrorAction SilentlyContinue

# 2. 生成分发包
# sdist: 源码分发版 source distribution
# bdist_wheel: 构建分发版 build distribution
python setup.py sdist bdist_wheel

# 3. 验证包结构
twine check dist/*
```
## 5. 发布到 PyPI
```
# 断开代理后上传到PyPI
# 在终端提示输入 Enter your API token: 时，只粘贴 token 本身，不要加上 pypi- 前缀（Twine 会自动加）
twine upload dist/*

# 测试上传命令
twine upload --repository testpypi dist/*
```
## 6. 安装验证
```
# 从PyPI安装
pip install mypackage

# 验证安装
python -c "import mypackage; print('成功安装版本:', mypackage.__version__)"
```
