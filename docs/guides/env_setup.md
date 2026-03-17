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
