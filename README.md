# AiWriter - AI小说写作助手

AiWriter是一个基于Python开发的AI辅助写作工具，帮助作者创作小说、设计角色，提高写作效率。

## 主要功能

- 🖊️ **智能写作**：基于人工智能模型辅助文学创作
- 👤 **角色生成**：自动创建丰富多样的人物角色
- 🔄 **故事结构优化**：分析并完善故事结构
- 📱 **跨平台支持**：Windows、macOS、Linux皆可使用

## 安装方法

### 基本要求

- Python 3.8+
- 虚拟环境（推荐）

### 安装步骤

1. 克隆代码库：

```bash
git clone https://github.com/yourusername/AiWriter.git
cd AiWriter
```

2. 创建并激活虚拟环境：

Windows:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 配置API密钥：

```bash
# 首次运行会提示设置API密钥
python main.py
```

## 使用方法

```bash
# 启动应用程序
python main.py
```

或者安装后使用：

```bash
# 安装到系统
pip install -e .

# 直接运行
aiwriter
```

## 配置说明

应用程序会在`data/configs/`目录下创建以下配置文件：

- `model_config.yaml` - AI模型配置
- `user_config.yaml` - 用户偏好设置
- `apikey.yaml` - API密钥存储（请勿分享此文件）

## 开发者指南

### 项目结构

```
AiWriter/
├── core/           # 核心功能模块
├── data/           # 数据文件
│   └── configs/    # 配置文件
├── docs/           # 文档
├── logs/           # 日志文件
├── modules/        # 功能模块
├── proxyserver/    # 代理服务器
├── src/            # 源代码
├── tests/          # 测试用例
├── ui/             # 用户界面
└── utils/          # 工具函数
```

### 运行测试

```bash
pytest tests/
```

## 贡献指南

欢迎贡献代码、报告问题或提出改进建议。请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '添加新功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请查看 [LICENSE](LICENSE) 文件

## 联系方式

如有问题或建议，请[提交Issue](https://github.com/yourusername/AiWriter/issues)或发送电子邮件至 your.email@example.com。

---

**AiWriter** - 让AI为您的创作插上翅膀 ✨ 