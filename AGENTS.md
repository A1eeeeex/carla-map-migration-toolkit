# AGENTS.md — CARLA Map Migration Toolkit

本文件是 Codex 在目标仓库中的长期工程规则。

## 1. 核心原则

```text
No inventory, no migration.
No baseline, no optimization.
No plan, no write.
No validation evidence, no success claim.
No cold-copy, no UE4.27 acceptance.
```

## 2. 产品边界

仓库只服务三条迁移路径：

- RoadRunner → Source CARLA
- Source CARLA → Package CARLA
- Source CARLA → vanilla UE4.27

修复、注意事项、性能优化、安全和验收属于迁移路径内部共享能力。不要把仓库扩展为通用地图平台、OpenDRIVE 编辑器、Apollo HDMap 工具、MCP 平台或 Unreal 通用 Agent。

## 3. 修改前必做

1. 读取本文件和目标 Skill 的 `SKILL.md`。
2. 运行 `git status --short`，保护无关脏文件。
3. 确认当前路线、源 Profile、目标 Profile、版本和执行上下文。
4. 读取现有 `map-workspace.json`、`map-handoff.json` 与阶段结果；没有则先建立只读 inventory。
5. 列出允许修改的路径和明确不修改的路径。
6. 对写操作生成 plan、备份和回滚点。

## 4. 路由边界

| 当前源 | 目标 | Skill |
|---|---|---|
| RoadRunner 导出 | Source CARLA | `roadrunner-to-source-carla` |
| Source CARLA | Package CARLA / 内容包 | `source-carla-to-package-carla` |
| Source CARLA | vanilla UE4.27 | `source-carla-to-ue427` |

发现请求属于另一条路线时，停止当前路线写入，交给正确 Skill；不要把三条流程串成错误的单一线性状态。

## 5. 执行上下文

每个脚本和命令必须声明以下之一：

- `host-cpython`
- `source-unreal-python`
- `ue427-unreal-python`
- `carla-client-python`
- `shell-build`

上下文不匹配必须快速失败并输出所需启动方式。禁止用普通 Python 假装执行 Unreal API，也禁止用不匹配的 CARLA Python client 验证服务器。

## 6. Unreal Asset 规则

- 不通过 OS 文件操作移动、重命名或删除 `.uasset`、`.umap`、`.uexp`、`.ubulk`。
- 使用 Unreal AssetTools、EditorAssetLibrary、Asset Registry、Migrate 和 redirector 修复流程。
- 删除或替换资产前必须查询 referencers。
- 对 CARLA 专用类执行替换时，记录原类、目标策略、受影响资产和验证结果。
- 未知版本或无法加载的二进制资产不得强制转换。

## 7. 写入和删除规则

- 默认 `inspect` / `plan`。
- 只有显式 `apply-safe` / `apply-plan` 才可写入。
- 所有路径 canonicalize 后必须位于允许根目录。
- 拒绝 `/`、`~`、空路径、未解析变量和根目录外路径。
- 替换目标前创建时间戳备份。
- 不运行 `git clean`、`git reset --hard`。
- 不递归删除工作区、CARLA 根或 UE 根。
- archive 解压前检查路径穿越、绝对路径、符号链接与异常成员。

## 8. 修复模块合同

每个修复模块必须实现：

```text
scan/detect
plan
apply
verify
rollback metadata
```

并输出稳定 reason code。不要只打印自然语言日志。

## 9. 性能优化规则

- 功能基线未通过时不优化。
- 保留 LOD0、材质槽、transform、道路几何、XODR 和可驾驶碰撞。
- 道路、车道线、交通设施、Route Planner、Trigger 和语义相关对象默认不可合并或删除。
- 高风险优化必须 `REVIEW_REQUIRED`。
- 前后测试必须同硬件、分辨率、质量、相机、交通和传感器负载。
- 报告 FPS 与 frame time，明确 VSync/cap。

## 10. 验证等级

| 等级 | 可以证明什么 |
|---|---|
| L0 结构验证 | Skill/Plugin/schema/链接格式有效 |
| L1 纯逻辑 | 路径、hash、archive、状态机和报告逻辑正确 |
| L2 Fixture | 假 CARLA 目录与假包工作流正确 |
| L3 Editor | Source CARLA 或 UE4.27 Editor 中真实执行成功 |
| L4 Runtime | Package CARLA / CARLA Python API / PIE 真实运行通过 |
| L5 Portability | 新环境或 cold-copy 通过 |

不得用较低等级证据冒充更高等级兼容性。

## 11. 报告规则

每次非平凡任务结束必须报告：

- 路线与 Profile；
- 环境和版本；
- 检测到的问题；
- 实际修改；
- 验证等级和结果；
- 证据文件；
- 未运行项与剩余风险；
- 备份和回滚方式。

`NOT_RUN` 不得显示为 PASS。

## 12. 公开仓库脱敏

禁止提交：

- 私有 discovery 报告中列出的任何客户、地图或项目标识；
- 任何本机 home、挂载点或内部绝对路径；
- CARLA/Unreal/RoadRunner 二进制和引擎文件；
- 客户地图、贴图、XODR、`.uasset/.umap/.uexp/.ubulk`；
- 完整运行日志、IP、token、用户名、内部服务器信息；
- 无明确再分发权利的 Demo 资产。

fixture 使用原创小文本、匿名 JSON、CSV、目录清单和 archive member list。

## 13. 测试与提交

- 先为旧行为建立 characterization test，再重构。
- 每个 reason code 至少有一个 fixture 或测试。
- Skill 描述修改后运行触发 eval。
- schema 修改需更新示例、迁移说明和版本。
- 每个 PR 保持一个可解释的工作包；不要混合大规模格式化、缓存清理和功能修改。
- 不 push、不发 Release，除非用户明确要求。
