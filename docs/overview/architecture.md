# 系统架构

## 总体架构

系统由五大模块组成，形成从感知到执行的完整闭环：

```mermaid
graph TB
    subgraph 感知层
        CAM[双目摄像头] --> YOLO[YOLO 器械检测]
        CAM --> CAL[手眼标定]
        YOLO --> GP[夹取点算法]
    end

    subgraph 语言层
        MIC[语音输入] --> ASR[语音识别]
        ASR --> NLP[Qwen2.5 器械名称识别]
    end

    subgraph 决策层
        GP --> VLA[OpenVLA 决策模型]
        NLP --> VLA
        VLA --> ACT[动作序列生成]
    end

    subgraph 执行层
        ACT --> MC[运动规划]
        MC --> CR5[越疆 CR5 机械臂]
        CR5 --> GRIP[夹爪控制]
        SAF[安全策略] --> CR5
    end

    subgraph 仿真层
        SIM[Isaac Sim] -.-> VLA
        SIM -.-> CR5
    end
```

## 模块职责

### 感知模块

- YOLO 目标检测：识别器械种类、位置
- 相机标定：手眼标定实现像素坐标到机械臂坐标的转换
- 夹取点算法：计算修正后的夹取位置和方向

### NLP 模块

- 基于 Qwen2.5-0.5B 微调的医疗器械实体识别模型
- 支持从语音转文字中提取器械名称并标准化输出

### 决策模块

- OpenVLA (Vision-Language-Action) 视觉-语言-动作模型
- 接收图像和任务指令，输出机器人动作序列
- LIBERO 仿真评测验证决策效果

### 执行模块

- 越疆 CR5 协作机械臂控制
- 运动规划与轨迹生成
- 安全策略（急停、碰撞检测、力反馈）

### 仿真模块

- Isaac Sim + Omniverse 构建虚拟手术室
- 支持 sim2real 迁移验证

## 数据流

```
语音指令 / 手动触发
       │
       ▼
  NLP 器械名称识别
       │
       ▼
  视觉感知（器械定位 + 夹取点计算）
       │
       ▼
  VLA 决策（生成动作序列）
       │
       ▼
  运动规划 → 机械臂执行 → 器械递交
       │
       ▼
  医生确认取走 → 完成
```

## 通信架构

| 接口 | 方式 | 说明 |
|------|------|------|
| 摄像头 → 感知 | USB / GigE | RGB-D 图像流 |
| 感知 → 决策 | Python API | 器械位置、夹取点坐标 |
| NLP → 决策 | Python API | 器械名称、标准化结果 |
| 决策 → 执行 | Python SDK | 目标坐标、动作序列 |
| 执行 → 机械臂 | Dobot SDK (TCP) | 关节角 / 末端位姿指令 |
