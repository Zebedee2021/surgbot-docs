# 开发环境搭建

## 服务器信息

| 配置项 | 规格 |
|-------|------|
| GPU 1 | NVIDIA RTX 4090 (48GB) |
| GPU 2 | NVIDIA Titan X (24GB) |
| 系统 | Ubuntu Linux |

## 基础环境

### 1. 克隆代码仓库

```bash
git clone https://github.com/YOUR_USERNAME/surgbot-code.git
cd surgbot-code
```

### 2. 创建 Conda 环境

根据所负责的模块，创建对应的环境：

=== "感知模块"

    ```bash
    conda create -n surgbot-perception python=3.10
    conda activate surgbot-perception
    pip install -r requirements.txt
    pip install -r perception/requirements.txt
    ```

=== "NLP 模块"

    ```bash
    conda create -n med_device_model python=3.10
    conda activate med_device_model
    pip install -r requirements.txt
    pip install -r nlp/requirements.txt
    ```

=== "决策模块"

    ```bash
    conda create -n surgbot-decision python=3.10
    conda activate surgbot-decision
    pip install -r requirements.txt
    pip install -r decision/requirements.txt
    ```

### 3. 验证环境

```bash
python scripts/check_gpu_env.py
```

## VS Code 远程开发配置

项目采用 VS Code Remote-SSH 连接工控机/服务器进行远程开发，在本地编辑代码，实时同步到远程环境。

### Remote-SSH 连接

1. 在 VS Code 中安装 **Remote - SSH** 插件
2. 在本地 `~/.ssh/config` 中添加服务器配置：

```
Host surgbot-server
    HostName <服务器IP>
    User <用户名>
    Port 22
    IdentityFile ~/.ssh/id_rsa
```

3. 通过 VS Code 左下角「远程连接」按钮选择目标服务器，即可在本地 VS Code 中直接编辑服务器上的代码

### 调试配置

在 `.vscode/launch.json` 中配置 Python 调试入口，可直接在 VS Code 中打断点调试机械臂运动。

=== "机械臂运动调试"

    配置 Python 调试入口指向 `main.py` 或机械臂运动控制脚本，可在运动规划、力控等关键代码行设置断点，实时观察关节角度和末端位姿。

=== "模块单独调试"

    各功能模块（感知、NLP、决策）可独立启动调试，无需启动完整系统。在 `launch.json` 中为各模块配置独立的调试入口。

### 自动化任务

通过 `.vscode/tasks.json` 配置常用操作，使用 `Ctrl+Shift+B` 快捷键一键执行：

- **构建环境** — 安装/更新依赖
- **运行测试** — 执行单元测试和集成测试
- **部署到机械臂** — 将代码同步到机械臂工控机
- **启动仿真** — 启动 Isaac Sim 仿真环境

项目目录结构详见 [系统架构 - 程序框架结构](../overview/architecture.md#程序框架结构)。

## GPU 环境检查

确保以下组件正确安装：

- CUDA / cuDNN
- PyTorch（支持 GPU）
- 各模块专属依赖

## 常见问题

### CUDA 版本不匹配

确认 PyTorch 安装版本与服务器 CUDA 版本对应。

### EGL / GLX 渲染问题

OpenVLA + LIBERO 评测需要图形渲染支持，服务器端需要配置 EGL 或 GLX。

## 开发模式说明

本项目采用的开发模式与传统嵌入式开发有本质区别：

| 对比维度 | 本项目 | 传统嵌入式 |
|---------|-------|-----------|
| 开发模式 | Linux + Python 服务化 + 事件驱动 | 裸机/RTOS + C 中断驱动 + 循环轮询 |
| 模块耦合 | 独立 Python 包，可单独测试和替换 | 紧耦合，改一处影响全局 |
| 调试方式 | VS Code Remote-SSH + 断点调试 + 日志 | 串口 / 仿真器 / JTAG |

!!! note "转型提示"
    对于有嵌入式开发背景的团队成员，需要适应服务化、模块化的开发思路。核心区别在于：每个模块是独立进程/包，通过接口通信而非共享内存；调试使用 VS Code 远程断点而非串口打印。
