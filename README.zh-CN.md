# CARLA 地图迁移工具包

本仓库只覆盖三条明确路线：

```text
RoadRunner    ── 导入与修复 ──► Source CARLA
Source CARLA ── Cook 与验证 ──► Package CARLA
Source CARLA ── 解耦与修复 ──► 原版 UE4.27
```

当前实现是实验性的 Codex Plugin 和确定性 host 核心。它能做只读发现、
路径与版本检查、不可变计划、archive 安全审计、性能证据比较和统一 JSON
报告；没有真实 Editor/runtime 证据时会保持 `NOT_RUN`。

本项目不附带客户地图、私有 XODR、Unreal/CARLA 二进制或引擎资产，也不是
CARLA、Epic Games 或 MathWorks RoadRunner 的官方项目。

## 安装与调用

v0.1 以完整 Plugin 为安装单位，不保证单独复制某个 Skill 子目录可用。三个
Skill 共享 scripts、schemas、profiles、templates 和 safety contracts。

```text
Use $roadrunner-to-source-carla. 先 inspect，再生成 plan，不要写入。
Use $source-carla-to-package-carla. 从 Source handoff 规划匹配平台的内容包。
Use $source-carla-to-ue427. 迁移到干净 UE4.27，并把 cold-copy 作为硬门禁。
```

## 当前证据

三条路线均只有 L0–L2 结构、纯逻辑和匿名 fixture 证据。Source/UE Editor、
Cook、Package 导入、CARLA runtime、PIE 和 UE4.27 cold-copy 均为 `NOT_RUN`，
因此没有任何版本组合标记为 `verified`，也不能称为 `v0.1.0-rc`。

运行开发测试：

```bash
python3 -m pip install --requirement requirements-dev.txt
python3 -m pytest -q
```

## 开发资料

可提交、已脱敏的开发资料统一放在
[`development/shared/`](development/shared/)；原始交接包、发现记录、草稿和
私有输入集中在 Git 忽略的 `development/local/`。新增资料前请阅读
[`development/README.md`](development/README.md)。

详细限制见 [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)，验证分层见
[VERIFICATION_STATUS.md](VERIFICATION_STATUS.md)。
