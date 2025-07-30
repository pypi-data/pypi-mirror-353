# Rcloud MCP Server python

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-0.1.0-green.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)

## 📌 项目简介

`rongcloud-server-mcp-python` 是基于 FastMCP 框架构建的 MCP 服务，集成了 [RongCloud 融云](https://www.rongcloud.cn/) 即时通讯能力，支持用户管理、消息发送、群组操作等功能。

---

## ✨ Tools

| 工具名称                      | 功能描述                                                        |
|-------------------------------|-----------------------------------------------------------------|
| `register_user`               | 通过融云注册新用户并返回该用户的 Token                          |
| `get_user_info`               | 使用融云接口获取用户信息                                       |
| `send_private_text_message`   | 发送私聊文本消息，返回每个接收用户对应的消息 ID                 |
| `send_group_text_message`     | 发送群聊文本消息，返回每个目标群组对应的消息 ID                 |
| `get_private_messages`        | 获取两个用户之间指定时间范围内的私聊历史消息                    |
| `create_group`                | 在融云中创建一个新的群聊，并指定初始成员                        |
| `dismiss_group`               | 永久解散一个融云群组                                           |
| `get_group_members`           | 获取融云中已存在群组的完整成员列表                              |
| `join_group`                  | 将一个或多个用户加入指定的融云群组                              |
| `quit_group`                  | 将一个或多个用户从融云群组中移除                                |
| `get_current_time_millis`     | 获取自 Unix 纪元（1970 年 1 月 1 日 UTC）以来的当前时间（以毫秒为单位）。 |


---

## ⚙️ 配置说明

### 🔧 环境变量

| 变量名                  | 是否必填 | 默认值                       | 描述                           |
|-----------------------|----------|------------------------------|--------------------------------|
| `RONGCLOUD_APP_KEY`    | ✅ 是    | -                            | 融云应用 App Key               |
| `RONGCLOUD_APP_SECRET` | ✅ 是    | -                            | 融云应用 App Secret            |
| `RONGCLOUD_API_BASE`   | ❌ 否    | `https://api-cn.ronghub.com` | 融云 API 基础 URL              |
| `RONGCLOUD_API_TIMEOUT`| ❌ 否    | `10`                         | API 请求超时时间（秒）         |
| `FASTMCP_LOG_LEVEL`    | ❌ 否    | `WARNING`                    | 日志级别（DEBUG、INFO 等）     |

### 🧪 示例配置

```env
RONGCLOUD_APP_KEY=your_app_key
RONGCLOUD_APP_SECRET=your_app_secret
RONGCLOUD_API_BASE=https://api-cn.ronghub.com
RONGCLOUD_API_TIMEOUT=10
FASTMCP_LOG_LEVEL=WARNING
````

### 💻 Claude Desktop 配置

* **配置文件路径**

  * macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
  * Windows: `%APPDATA%/Claude/claude_desktop_config.json`

* **配置示例**：

```json
{
  "mcpServers": {
    "rongcloud-server-mcp": {
      "command": "uvx",
      "args": [
        "rongcloud-server-mcp-python"
      ],
      "env": {
        "RONGCLOUD_APP_KEY": "your_app_key",
        "RONGCLOUD_APP_SECRET": "your_app_secret",
        "RONGCLOUD_API_BASE": "https://api-cn.ronghub.com",
        "RONGCLOUD_API_TIMEOUT": "10"
      }
    }
  }
}
```

---

## 🧑‍💻 开发指南

### 🚀 快速开始

1. 克隆仓库并进入项目目录：

   ```bash
   git clone https://github.com/你的用户名/rcloud-server-mcp-python.git
   cd rcloud-server-mcp-python
   ```

2. 复制示例配置文件并编辑环境变量：

   ```bash
   cp .env.example .env
   ```

   编辑 `.env` 文件，填写如下内容：

   ```env
   RONGCLOUD_APP_KEY=your_app_key
   RONGCLOUD_APP_SECRET=your_app_secret
   RONGCLOUD_API_BASE=https://api-cn.ronghub.com
   FASTMCP_LOG_LEVEL=INFO
   ```

3. 创建虚拟环境，安装依赖并启动开发服务器：

   ```bash
   make venv
   make sync
   make install
   make dev
   ```

> 💡 你可以运行 `make help` 查看所有可用命令。

---

### ✅ 运行测试

```bash
make test     # 运行所有测试
make lint     # 代码风格和质量检查
make fix      # 自动修复格式问题
```

---

## 🤝 贡献指南

欢迎贡献代码！请按照以下步骤：

1. Fork 本项目
2. 创建新分支：`git checkout -b feature/YourFeature`
3. 提交更改：`git commit -m 'Add YourFeature'`
4. 推送分支：`git push origin feature/YourFeature`
5. 提交 Pull Request

> 请确保代码通过以下检查：
>
> * `make lint` 无错误
> * `make test` 全部通过
> * `make format` 代码格式整齐

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可。

