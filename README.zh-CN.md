# CARLA 地图迁移工具包

三项 Codex Skill，帮助你导入、打包和交付自定义 CARLA 地图。

```text
RoadRunner    ── 导入与修复 ──► Source CARLA
Source CARLA ── Cook 与验证 ──► Package CARLA
Source CARLA ── 解耦与修复 ──► 原版 UE4.27
```

[English](README.md) · [安装说明](docs/installation.md) · [能力清单](docs/capabilities.md) · [实测与限制](docs/current-status.md)

这是一个实验性的 Codex Plugin：把地图处理经验整理成操作流程，配合检查、
规划、包体审计和性能比较脚本，帮助 Codex 按步骤处理常见问题。
它不是一键地图转换器；导入、修复、构建和实际运行，仍需要你自己的引擎环境
以及经过授权的编辑器/API 操作。

## 选择你要做的事

| 你的目标 | 使用指南 |
|---|---|
| 把 RoadRunner 导出地图放进 Source CARLA 编辑 | [导入与修复](docs/routes/roadrunner-to-source-carla.md) |
| 把 Source 地图打包，交给匹配的发行版 CARLA | [Cook 与打包](docs/routes/source-carla-to-package-carla.md) |
| 去除 CARLA 依赖，交付给原版 UE4.27 | [迁移与干净复制验收](docs/routes/source-carla-to-ue427.md) |

三条路线共享材质、贴图、引用、碰撞、晴天显示、Content-only 交付和分阶段
性能优化指引。脚本可以审计压缩包、生成 SHA256 文件清单，并如实列出性能
改善与退化。哪些自动完成、哪些需要编辑器操作，见[能力清单](docs/capabilities.md)。

## 安装

已测试环境：Ubuntu 22.04 x86_64、Python 3.10.12、Codex CLI 0.153.4。
版本检查与详细步骤见[安装说明](docs/installation.md)。请安装完整 Plugin，
不要只复制某个 Skill 文件夹；三项 Skill 需要共享脚本、格式定义和参考资料。
以下安装命令使用 `shell-build` 上下文。

```bash
git clone https://github.com/A1eeeeex/carla-map-migration-toolkit.git
cd carla-map-migration-toolkit
python3.10 -m venv .venv
.venv/bin/python -m pip install --requirement requirements-runtime.txt
codex plugin marketplace add . --json
codex plugin add carla-map-migration-toolkit@carla-map-migration-toolkit --json
source .venv/bin/activate
codex
```

## 在 Codex 中使用

选一条请求，补充你的输入文件位置，从只读检查开始：

```text
Use $carla-map-migration-toolkit:roadrunner-to-source-carla. 检查我的 RoadRunner 导出文件，规划导入 Source CARLA。先不要修改文件。
```

```text
Use $carla-map-migration-toolkit:source-carla-to-package-carla. 检查我的 Source CARLA 交接资料，规划匹配平台的地图内容包。先不要构建或安装。
```

```text
Use $carla-map-migration-toolkit:source-carla-to-ue427. 检查我的 Source CARLA 地图，规划交付到干净 UE4.27，并安排第二个干净项目的复制验收。先不要修改文件。
```

没有引擎和地图也可以试用。在另一个终端进入克隆目录，运行
[纯文本演示](demo/quickstart/README.md)：

```bash
demo_root="$(mktemp -d -t cmtk-quickstart.XXXXXX)"
.venv/bin/python demo/quickstart/run_demo.py --workspace-root "$demo_root"
```

预期输出：`demo_status: PASS`、`route_validation_status: NOT_RUN`。
意思是计划逻辑检查通过，真实地图导入没有执行，不是报错。

## 实际验证到什么程度？

[提交 6222f0c 的 435 项自动测试全部通过](https://github.com/A1eeeeex/carla-map-migration-toolkit/actions/runs/34193021128)，
覆盖结构、主机脚本逻辑和模拟数据；引擎测试在该次 CI 中跳过。
三条路线也都有历史实操记录，包括第二个 UE4.27 项目检查和 Content-only
交付。但这些是特定案例，不代表所有地图和版本都兼容；按工具包现行格式记录
的完整端到端证据仍未齐，因此当前是实验版，不是已严格验收的 RC。

实测范围与缺口统一见[当前状态](docs/current-status.md)。默认先检查、再规划；
修改资产需明确授权、引擎适用的备份和实际验证，高风险优化需要审查。
仓库不提供客户地图、XODR 或引擎二进制。

## 按需阅读

- [已知限制](KNOWN_LIMITATIONS.md)：尚未实现或不支持的行为
- [贡献指南](CONTRIBUTING.md)：开发环境与修改要求
- [开发参考索引](development/shared/README.md)：设计、证据规则和历史报告
- [更新记录](CHANGELOG.md)：开发与版本历史

<details>
<summary>开发者测试命令</summary>

在克隆目录运行：

```bash
.venv/bin/python -m pip install --requirement requirements-dev.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -m pytest -q -p no:cacheprovider
```

不通过 Codex 调用的 `host-cpython` 命令示例见英文首页和安装说明。

</details>

---

## 许可与联系

[Apache-2.0](LICENSE) · [署名声明](NOTICE.md) · [引用信息](CITATION.cff) · 维护者 [@A1eeeeex](https://github.com/A1eeeeex)。
许可证仅覆盖本项目有权发布的原创材料，不授予第三方地图或引擎的使用权。
本项目独立于 CARLA、Epic Games 和 MathWorks RoadRunner，不代表官方或获得
其背书。安全问题请遵循 [SECURITY.md](SECURITY.md)，不要在公开 Issue 披露敏感细节。
