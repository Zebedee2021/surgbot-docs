# 数据集管理

## 核心原则

!!! warning "重要"
    **数据集和模型权重不入 Git 仓库。** 仓库中只存放数据处理脚本和数据说明文档。

## 数据存储位置

所有数据集和模型权重存放在实验室 NAS / 云盘：

```
/surgical-robot-data/
├── yolo_dataset/       # YOLO 训练数据（图片 + 标注）
├── nlp_dataset/        # NLP 标注数据（JSON 格式）
├── vla_dataset/        # VLA 格式数据（.npy / RLDS）
├── sim_dataset/        # 仿真采集数据
└── model_weights/      # 训练好的模型权重
    ├── qwen2.5-med-device/
    ├── openvla-finetuned/
    └── yolo-instruments/
```

## 仓库中的数据相关文件

```
surgbot-code/
├── scripts/
│   ├── data_download.sh        # 从 NAS 下载数据的脚本
│   └── dataset_prepare.py      # 数据预处理流水线
└── docs/
    └── dataset_guide.md        # 数据集说明文档
```

## 数据使用流程

1. 首次使用：运行 `scripts/data_download.sh` 从 NAS 下载数据到本地
2. 数据预处理：运行 `scripts/dataset_prepare.py` 处理原始数据
3. 训练：各模块的训练脚本指向本地数据目录

## 数据版本管理

- 数据集每次更新时，在 NAS 上按日期创建快照目录
- 在仓库的 `docs/dataset_guide.md` 中记录数据集版本变更
- 训练实验中记录使用的数据集版本

## .gitignore 保护

代码仓库的 `.gitignore` 已配置排除所有常见数据和模型文件格式：

```
*.npy *.npz *.tfrecord *.hdf5 *.h5
*.pt *.pth *.safetensors *.bin
datasets/ data/ models/ checkpoints/
```
