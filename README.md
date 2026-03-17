# 手术器械护士机器助手 - 项目文档

**雄安宣武医院神经外科** x **北京理工大学具身空间智能实验室** (Embodied Space & AI Lab)

> 本仓库为项目文档站源码，基于 MkDocs + Material 主题构建，通过 GitHub Pages 自动部署。

**文档站地址**: https://zebedee2021.github.io/surgbot-docs/

## 项目简介

手术器械护士机器助手是一款面向神经外科手术室的辅助系统，定位为**配合器械护士和医生**，承担高频、标准化的器械识别、抓取和递交任务。当前阶段不是取代器械护士，而是通过人机协同减轻护士负担、提升手术安全性和效率。

### 系统模块

| 模块 | 核心技术 |
|------|---------|
| 感知模块 | YOLO 器械检测、手眼标定、夹取点算法 |
| NLP 模块 | Qwen2.5-0.5B 器械名称识别 (SFT + DPO) |
| 决策模块 | OpenVLA 视觉-语言-动作模型 |
| 执行模块 | 越疆 CR5 协作机械臂控制 |
| 仿真模块 | Isaac Sim + Omniverse 虚拟手术室 |

## 文档结构

```
docs/
├── overview/        # 项目总览（简介、架构、团队、硬件、人机协同方案）
├── modules/         # 模块文档（感知 / NLP / 决策 / 执行 / 仿真）
├── progress/        # 项目进展与里程碑
├── meeting/         # 会议记录
├── testing/         # 测试计划与记录
├── members/         # 成员工作总结
├── references/      # 参考论文与领域知识
└── guides/          # 操作指南（Git 入门、环境搭建、数据管理）
```

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 本地预览（热重载）
mkdocs serve

# 构建静态站点
mkdocs build
```

## 部署

推送到 `main` 分支后，GitHub Actions 自动构建并部署到 GitHub Pages (`gh-pages` 分支)。

## 协作规范

1. 创建特性分支: `git checkout -b docs/修改描述`
2. 编辑 `docs/` 下的 Markdown 文件
3. 提交: `git commit -m "docs: 修改描述"`
4. 推送并创建 Pull Request

详见文档站 [Git 快速入门](https://zebedee2021.github.io/surgbot-docs/guides/git_quickstart/)。
