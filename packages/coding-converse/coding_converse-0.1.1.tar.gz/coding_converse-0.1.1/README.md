# CodingConverse MCP Server

一个为AI代码编辑器提供用户对话能力的MCP (Model Context Protocol) 服务。当AI编辑器需要与用户交互时，可以通过此服务显示对话框获取用户输入。

## 特性

- 🤖 **MCP协议支持**: 完全兼容MCP 2024-11-05协议
- 💬 **用户对话**: 为AI编辑器提供与用户交互的能力
- 🎨 **现代UI**: 基于PyQt6的专业对话框界面
- 🚀 **易于集成**: 支持Cursor、Windsurf、Trae等AI编辑器
- 📡 **stdio通信**: 通过标准输入输出与AI编辑器通信

## 安装

### 方法1: 从源码安装（推荐）

```bash
# 克隆项目
git clone https://github.com/yourusername/coding-converse.git
cd coding-converse

# 安装依赖
pip install -r requirements.txt

# 安装为可编辑包
pip install -e .
```

### 方法2: 直接安装

```bash
# 直接从源码安装
pip install .
```

### 验证安装

```bash
# 测试模块导入
python -c "import coding_converse; print('安装成功')"

# 运行测试
python test_module.py
```

## 在AI编辑器中配置

### Cursor / Windsurf / Trae AI

在编辑器的MCP配置文件中添加：

```json
{
  "mcpServers": {
    "CodingConverse": {
      "command": "python",
      "args": [
        "-m",
        "coding_converse"
      ],
      "env": {}
    }
  }
}
```

或者如果已安装为包：

```json
{
  "mcpServers": {
    "CodingConverse": {
      "command": "coding-converse",
      "args": [],
      "env": {}
    }
  }
}
```

## 使用方法

### 直接运行服务器

```bash
# 方法1: 作为模块运行
python -m coding_converse

# 方法2: 直接运行服务器文件
python server.py

# 方法3: 如果已安装为包
coding-converse
```

### 在AI编辑器中使用

配置完成后，AI编辑器可以使用 `ask_user` 工具与用户交互：

```python
# AI编辑器会调用这个工具
ask_user(
    message="遇到了一个问题，需要您的建议：应该使用哪种数据结构？",
    title="AI编辑器询问",
    placeholder="请输入您的建议..."
)
```

## MCP工具

### `ask_user`

向用户显示对话框并获取输入。

**参数:**
- `message` (string, 必需): 要向用户显示的消息内容
- `title` (string, 可选): 对话框标题，默认为"AI编辑器询问"
- `placeholder` (string, 可选): 输入框占位符，默认为"请输入您的回复..."

**返回值:**
- 用户输入的文本内容

## 使用场景

- 🤔 **方案选择**: AI需要用户在多个技术方案中选择
- 🐛 **问题诊断**: 遇到复杂问题时向用户询问更多信息
- ⚙️ **配置确认**: 确认重要的配置更改
- 📝 **需求澄清**: 当需求不明确时获取用户澄清
- 🔧 **调试协助**: 请求用户提供调试信息

## 系统要求

- Python 3.8+
- PyQt6 6.4.0+
- 支持MCP协议的AI编辑器

## 开发

```bash
# 开发模式安装
pip install -e .

# 运行测试
python -c "from message_dialog import show_message_dialog; print(show_message_dialog('测试消息'))"
```

## 许可证

MIT License

## 贡献

欢迎提交问题和拉取请求！