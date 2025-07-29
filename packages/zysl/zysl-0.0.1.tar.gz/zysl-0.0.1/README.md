## 构建依赖包

### 基础命令

```shell
python setup.py sdist bdist_wheel
python -m build
pip install -e .[dev]
```

### 构建命令

```shell
rm -rf './dist'
python -m build
twine upload dist/*
```

