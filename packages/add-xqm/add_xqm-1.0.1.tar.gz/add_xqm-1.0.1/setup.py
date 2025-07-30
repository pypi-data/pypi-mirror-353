import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="add_xqm",
    version="1.0.1",
    author="yunyi",
    url='https://github.com/hujinpu/add_xqm',
    author_email="2523863783@qq.com",
    description="xxx",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)