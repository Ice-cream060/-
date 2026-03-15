简面 Pro | Resume Architecture Engine
简面 Pro 是一款基于 PyQt6 开发的交互式简历生成工具，旨在为追求品质的求职者提供“高管级”的简历构建体验。它打破了传统填表式简历工具的枯燥，采用 可视化节点流 (Workflow Nodes) 交互方式，并结合 DeepSeek AI 进行精准的岗位匹配润色。

✨ 核心特性
🎨 沉浸式交互画布：采用类 Figma/Notion 的节点式交互，支持自由拖拽、动态连线，让简历构建如同搭建逻辑架构图。

🧠 DeepSeek AI 深度赋能：内置高级简历优化算法。根据用户设定的“理想职业”，AI 会自动修正病句、提炼 STAR 法则描述，并将琐碎经历转化为具有业务价值的职场语言。

📸 智能职业肖像引擎：内置图像裁剪组件，支持用户手动选取并精准裁剪正方形职业照，自动集成至最终 PDF 导出文档。

🎭 动态主题引擎：支持“极客黑”、“优雅白”、“樱花粉”等多种 UI 主题一键切换。

📄 殿堂级 PDF 渲染：基于 wkhtmltopdf 引擎，采用 66/34 黄金比例分栏设计，支持中英双语标题对照，并完美解决 PDF 分页截断问题。

🛠️ 技术栈
GUI 框架: PyQt6 (QGraphicsView 架构)

AI 引擎: DeepSeek API (OpenAI SDK 兼容)

导出引擎: pdfkit + wkhtmltopdf

数据格式: Base64 图像编码, HTML5/CSS3 模板渲染

🚀 快速开始
1. 环境准备
确保你的电脑已安装 Python 3.8+，并安装以下依赖：

Bash

pip install PyQt6 openai python-docx pdfkit
2. 安装渲染引擎
本项目 PDF 生成依赖于 wkhtmltopdf。

下载并安装 wkhtmltopdf。

重要提示：代码中默认指向 D:\wkhtmltopdf\bin\wkhtmltopdf.exe。如果你的安装路径不同，请在 main.py 的 generate_pdf 函数中修改 path_wkhtmltopdf 变量。

3. 配置 AI 密钥
在 DeepSeekWorker 类中配置你的 API Key：

Python

api_key="你的 sk-key"
4. 运行
Bash

python main.py
📖 使用指南
职业引导：启动程序后，输入你的“理想职业”。这非常重要，因为 AI 会根据该职业定制所有的润色建议。

构建架构：在下方工具栏点击模块（如“项目经历”），画布会生成对应节点。

智能润色：双击节点打开编辑抽屉，输入原始文本后点击 “DeepSeek 智能润色”，AI 会通过 20 年经验的专家视角重构内容。

生成导出：点击右上角“生成 PDF 文档”，一份精美的简历将直接保存至你的桌面。

🤝 贡献与反馈
本项目由你开发并维护。如果你在使用过程中发现了 Bug 或有更好的功能建议，欢迎通过 GitHub Issue 提交。

“助力每一个为写简历而烦恼的小孩。” —— 简面 Pro
