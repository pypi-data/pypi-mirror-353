# mcp_test_czhsb

阿里百炼 MCP 服务测试工具

## 功能

在用户输入后添加"我收到了"

## 安装

```bash
pip install mcp_test_czhsb
```

## 使用方法

在阿里百炼平台配置 MCP 服务：

```python
from mcp_test_czhsb import process_input

# 在百炼平台会自动注册为工具
```

## 示例

输入: "你好"
输出: "你好，我收到了"

输入: "测试 123"
输出: "测试 123，我收到了"
