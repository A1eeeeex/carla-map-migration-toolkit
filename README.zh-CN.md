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

想快速了解能干什么，先看[通俗能力清单](docs/capabilities.md)：包括三条迁移
路线、Content-only 交付审计、SHA256 清单、故障处理和性能优化，并明确区分
“脚本自动完成”和“需要编辑器实际操作”的部分。

本项目不附带客户地图、私有 XODR、Unreal/CARLA 二进制或引擎资产，也不是
CARLA、Epic Games 或 MathWorks RoadRunner 的官方项目。

## 安装与调用

v0.1 以完整 Plugin 为安装单位，不保证单独复制某个 Skill 子目录可用。三个
Skill 共享 scripts、schemas、profiles、templates 和 safety contracts。

在受支持主机的全新 clone 中以 `shell-build` 上下文执行；插件内确定性命令
使用 `host-cpython`：

```bash
python3.10 -m venv .venv
.venv/bin/python -m pip install --requirement requirements-runtime.txt
codex plugin marketplace add . --json
codex plugin add carla-map-migration-toolkit@carla-map-migration-toolkit --json
```

准确版本范围、验证命令、限制和五分钟流程见
[安装合同](docs/installation.md)。

不安装 CARLA/Unreal、也不使用任何客户资产即可运行
[安全快速演示](demo/quickstart/README.md)：

```bash
demo_root="$(mktemp -d -t cmtk-quickstart.XXXXXX)"
.venv/bin/python demo/quickstart/run_demo.py --workspace-root "$demo_root"
```

它会通过只读检查和计划哈希校验，然后按预期把真实运行验证标为
`NOT_RUN`。这证明的是 L1 host 逻辑，不是地图已经成功导入。

```text
Use $carla-map-migration-toolkit:roadrunner-to-source-carla. 先 inspect，再生成 plan，不要写入。
Use $carla-map-migration-toolkit:source-carla-to-package-carla. 从 Source handoff 规划匹配平台的内容包。
Use $carla-map-migration-toolkit:source-carla-to-ue427. 迁移到干净 UE4.27，并把 cold-copy 作为硬门禁。
```

## 当前证据

这里要区分两种状态：

| 范围 | RoadRunner→Source | Source→Package | Source→UE4.27 |
|---|---|---|---|
| 已记录真实操作 | Source 编辑器检查与限定平面道路驾驶验证 | 包体、安装一致性和 runtime 记录 | 第二干净项目结构、PIE、晴天视图和 Content-only 交付记录 |
| 当前完整证据合同 | 尚无完整 L4 Verified Run | 尚无完整 L5 Verified Run | 已有目标阶段证据；尚无完整新版 L5 Verified Run |

三条路线及其修复/优化工作都有实测记录，覆盖范围和限制各不相同。较新的
记录也包含第二干净 UE4.27.2 项目、晴天视图和 Content-only 交付；之前
“cold-copy 尚未做过”的说明已经过时。这里的完整新版 Verified Run 仍未齐，
不会把旧记录换个格式就宣布通过，也不据此承诺所有地图或版本兼容。
详见[当前状态](docs/current-status.md)、[发布清单](docs/release-readiness.md)、
[历史路线绑定](development/shared/release-research/historical-evidence-binding-summary.md)
和[修复/优化证据摘要](development/shared/release-research/historical-repair-optimization-evidence-summary.md)。
需要严格新版证据时，使用[执行上下文适配器](docs/evidence-adapters.md)。

材质修复后的同条件 LOD 复测也已完成：平均帧率、平均/尾部帧时间和 GPU
时间均有改善，但中位帧时间只改善 0.56%，未达到预先封存的 3% 自动门槛，
因此结论仍是 `REVIEW_REQUIRED`，不能宣传成通用或 Package runtime 性能结论。

运行开发测试：

```bash
.venv/bin/python -m pip install --requirement requirements-dev.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -m pytest -q -p no:cacheprovider
```

## 开发资料

可提交、已脱敏的开发资料统一放在
[`development/shared/`](development/shared/)；原始交接包、发现记录、草稿和
私有输入集中在 Git 忽略的 `development/local/`。新增资料前请阅读
[`development/README.md`](development/README.md)。

## 许可证

本项目有权发布的原创材料采用 [Apache License 2.0](LICENSE)，版权与署名信息
记录在 [NOTICE](NOTICE.md) 和 [CITATION.cff](CITATION.cff)。该许可证不授予
对 CARLA、Unreal Engine、RoadRunner、客户材料、私有输入、排除的二进制或
第三方资产的权利。

公开维护者为 [@A1eeeeex](https://github.com/A1eeeeex)。安全问题必须使用
[SECURITY.md](SECURITY.md) 中的私密流程，不要在公开 Issue 中披露细节。

详细限制见 [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)，验证分层见
[VERIFICATION_STATUS.md](VERIFICATION_STATUS.md)。
