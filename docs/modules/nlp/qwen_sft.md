# Qwen2.5 SFT 微调

## 环境配置

基础环境：Linux 服务器（Ubuntu, RTX 4090 48GB），使用 conda 创建专属环境：

```bash
# 创建 conda 环境
conda create -n med_device_model python=3.10
conda activate med_device_model

# 安装依赖
pip install torch==2.1.0 transformers==4.36.2 datasets==2.14.6

# 安装 LlamaFactory（模型微调核心工具）
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e .[all]
```

## 指令微调模板设计

针对院内不同场景（病历文本识别、语音转文字识别、台账文本匹配）设计指令模板：

```json
{
  "messages": [
    {
      "role": "system",
      "content": "你是一个专业的医疗领域AI助手。你的任务是从用户的文本中准确提取出所有的'手术器械'名称。"
    },
    {
      "role": "user",
      "content": "提取医疗工具：给我直角钩"
    },
    {
      "role": "assistant",
      "content": "直角钩"
    }
  ]
}
```

## 微调参数

| 参数 | 值 |
|------|-----|
| 微调方式 | LoRA 轻量化微调 |
| 框架 | LlamaFactory SFT 模块 |
| 评估指标 | F1 值、精确率 |

## 调优策略

通过控制变量法调整学习率、训练轮数等参数，在验证集上的实体识别 F1 值中选择最优超参数组合。
