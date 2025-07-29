from setuptools import setup, find_packages

setup(
    name="mcp_test_czhsb",
    version="0.1.0",  # 更新版本号
    packages=find_packages(exclude=['myenv', 'myenv.*']),
    install_requires=[],
    description="MCP服务测试 - 在用户输入后添加'我收到了'",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/czhsb/mcp_test_czhsb",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)