# Git 快速入门

本指南面向团队成员，帮助快速上手 Git 和 GitHub 协作。

## 安装 Git

### Windows

下载安装 [Git for Windows](https://git-scm.com/download/win)，安装时使用默认选项即可。

### 配置用户信息

安装完成后，打开终端（Git Bash 或 PowerShell），配置你的用户名和邮箱：

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

## 日常工作流（6 条命令）

### 第 1 步：拉取最新代码

每天开始工作前，先拉取最新代码：

```bash
git pull
```

### 第 2 步：创建特性分支

不要直接在 main 上修改代码，创建一个新分支：

```bash
git checkout -b feat/我的功能描述
```

分支命名规则：

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feat/` | 新功能 | `feat/perception-grasp-correction` |
| `fix/` | 修复问题 | `fix/calibration-timeout` |
| `docs/` | 文档修改 | `docs/add-meeting-0305` |
| `exp/` | 实验性代码 | `exp/openvla-lora-tuning` |

### 第 3 步：暂存改动

修改代码后，暂存所有改动：

```bash
git add .
```

### 第 4 步：提交

```bash
git commit -m "feat: 添加夹取点修正算法"
```

提交消息格式：`类型: 简要描述`

| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | feat: 添加夹取点修正算法 |
| fix | 修复问题 | fix: 修复标定超时问题 |
| docs | 文档更新 | docs: 更新2月现场测试总结 |
| data | 数据/脚本 | data: 添加器械数据集预处理脚本 |
| exp | 实验记录 | exp: OpenVLA LoRA 学习率 1e-4 |

### 第 5 步：推送到远程

```bash
git push -u origin feat/我的功能描述
```

### 第 6 步：创建 Pull Request

在 GitHub 网页上：

1. 点击 "Compare & pull request" 按钮
2. 填写 PR 描述（做了什么、关联哪个 Issue）
3. 指定一位队友 Review
4. 等待 Review 通过后点击 "Squash and merge"

## 遇到冲突怎么办

1. 先拉取最新代码：`git pull origin main`
2. 解决冲突文件中的 `<<<<<<` 标记
3. `git add .` → `git commit` → `git push`
4. 如果搞不定 → **不要 force push**，找队友一起看

## 重要提醒

!!! danger "禁止操作"
    - **不要**直接在 main 分支上修改和推送代码
    - **不要**使用 `git push --force`
    - **不要**提交数据集、模型权重等大文件
