# 个人身份发布开源项目：姓名、隐私与常见流程

Research date: 2026-08-28\
Execution context: `host-cpython`\
Scope: 个人将本仓库发布为开源项目时的公开身份与发布流程。本文只整理官方资料，
不构成法律意见，也不授权公开仓库、推送或发布 Release。

## 结论

**在 GitHub 上以个人身份公开项目，并不等于必须公开真实姓名。** GitHub 当前条款只把
有效邮箱列为普通账号注册必需信息，并明确把真实姓名列为可选信息（代表法律实体接受条款
或使用付费账号等情形除外）。GitHub 也明确允许为了隐私把任意文本设为 Git 提交作者名，
并提供 `noreply` 提交邮箱。因此，公开 GitHub 用户名、提交作者名和公开邮箱都可以与个人
法定姓名、私人邮箱分离。[GitHub Terms of Service §B.2](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service#2-required-information),
[Setting your username in Git](https://docs.github.com/en/get-started/git-basics/setting-your-username-in-git),
[Email addresses reference](https://docs.github.com/en/account-and-profile/reference/email-addresses-reference)

但“平台不要求实名”不能推出“版权权利人可以随意填写”。开源许可必须由版权权利人或其
授权者授予。WIPO 说明软件通常自动受到版权保护、第一权利人通常是创作者，但雇佣关系等
存在依国家法律而异的例外；自愿登记还可能帮助证明所有权。换言之，发布前最重要的是确认
代码和文档的权利来源，而不是先决定展示名。[WIPO Copyright FAQ](https://www.wipo.int/en/web/copyright/faq-copyright)

常用许可证的官方文本要求标明权利人，但没有规定“必须填写政府证件上的姓名”：MIT 文本
使用 `<COPYRIGHT HOLDER>`；Apache-2.0 把 Licensor 定义为版权权利人或获其授权的实体，
其应用模板使用 `[name of copyright owner]`。这只能证明许可证模板没有设定证件实名格式，
**不能证明假名在所有法域的确权、维权或税务场景中都等同于法定姓名**。
[OSI MIT License](https://opensource.org/license/mit),
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.html),
[ASF licensing FAQ](https://www.apache.org/foundation/license-faq.html#MayIApplyALv2ToMyOwnSoftware)

因此，对希望认真维护项目的个人，较稳妥的默认做法是：

- GitHub 账号、日常提交和公开联系渠道可以使用稳定昵称及 `noreply` 邮箱；
- `LICENSE`/版权声明使用真实且有权授权的权利人标识。愿意公开时，个人法定姓名最清晰；
  不愿公开时，不应由工程流程擅自断定昵称在适用法域足够，应先确认当地规则或取得专业意见；
- 不要把尚未成立、也未取得权利的项目名或 GitHub Organization 填成版权权利人；
- 项目显示作者、引用作者、维护者、安全联系人和版权权利人可以是不同字段，不必强行合一。

## 哪些信息可以不公开

| 信息 | GitHub/格式要求 | 可采用的隐私做法 |
|---|---|---|
| GitHub 真实姓名 | 普通免费个人账号不要求公开真实姓名 | 只显示账号名或稳定昵称 |
| Git 提交作者名 | GitHub 明确允许任意文本 | 为本仓库单独配置稳定昵称；只影响后续提交 |
| 提交邮箱 | 需要可用邮箱管理账号，但提交可使用 GitHub `noreply` | 开启邮箱隐私并用 ID-based `noreply` 地址 |
| `CITATION.cff` 作者 | `authors` 必填；CFF 1.2.0 支持个人、实体、`alias`，也明确示范 `name: anonymous` | 使用稳定 alias 或匿名实体；个人 `email` 是可选字段 |
| 安全报告邮箱 | GitHub 不要求在仓库公开私人邮箱 | 仓库公开后启用 Private vulnerability reporting；`SECURITY.md` 写清入口 |
| 电话、地址、证件号 | 本项目发布流程不需要 | 不写入仓库、提交历史、Issue 或发布材料 |

CFF 的这些能力属于**引用元数据**，不能替代版权归属判断；`name: "project
contributors"` 可以是结构有效的引用作者，但并不能自动把该群体变成版权权利人。
[CFF 1.2.0 schema guide](https://github.com/citation-file-format/citation-file-format/blob/1.2.0/schema-guide.md#authors),
[CFF person/alias fields](https://github.com/citation-file-format/citation-file-format/blob/1.2.0/schema-guide.md#definitionsperson),
[CFF guidance for anonymous authors](https://github.com/citation-file-format/citation-file-format/blob/1.2.0/schema-guide.md#how-to-deal-with-unknown-individual-authors)

GitHub 的 Private vulnerability reporting 可让任何人向公开仓库维护者私下提交漏洞，
无需暴露个人邮箱；它与 `SECURITY.md` 是两个独立机制。若未启用该功能，GitHub 建议依
`SECURITY.md` 的指引联系维护者。[Privately reporting a security vulnerability](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately),
[Adding a security policy](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/add-security-policy)

## 个人发布的常见流程

1. **确认权利。** 清点原创代码、文档、历史提交和第三方材料；确认没有客户地图、私有资产、
   Unreal/CARLA 二进制或无再分发权内容。若内容可能来自雇佣、委托或多人协作，先确认谁
   能授权。公开在互联网本身不会把作品变成公共领域，也不会补足缺失授权。
   [WIPO Copyright FAQ](https://www.wipo.int/en/web/copyright/faq-copyright)
2. **决定公开身份边界。** 分别决定 GitHub 展示名、Git 提交名、版权权利人、引用作者、维护者
   和安全渠道。先配置提交昵称与 `noreply`，再生成将进入公开历史的新提交。
   [GitHub commit email guidance](https://docs.github.com/en/account-and-profile/concepts/email-addresses#commit-email-addresses)
3. **选择并准确加入许可证。** 没有许可证时，默认版权规则仍适用，访客不能据此自由使用、
   修改和分发；GitHub 因此把许可证视为项目真正开源的必要条件，并建议在仓库根目录放置
   `LICENSE` 文件。不要自行改写标准许可证正文。
   [Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
4. **同步公开元数据。** 让 `LICENSE`、`NOTICE`、`README`、`CITATION.cff`、Plugin manifest
   和维护文档对项目名、版本、作者/权利人角色保持一致；`SECURITY.md` 只公布必要的报告
   方法。若使用 Apache-2.0，按其官方文本处理现有归属声明和 `NOTICE`，不要把 NOTICE 当作
   任意宣传页。[Apache License 2.0 §4](https://www.apache.org/licenses/LICENSE-2.0.html#redistribution)
5. **在私有状态完成门禁。** 扫描当前树、完整 Git 历史、全部远端 refs 和 CI/Actions 产物；
   从干净环境验证安装、测试、最小匿名演示和卸载/回滚。身份决定不能替代这些技术与脱敏
   证据。
6. **最后才公开。** 在所有门禁通过并获得明确授权后，先公开仓库，再验证匿名访问和许可证
   检测；之后才创建不可变预发布标签/Release。GitHub 提醒，公开仓库会授予其他 GitHub
   用户通过平台查看和 fork 内容的权利，因此可见性切换不是可忽略的试运行步骤。
   [GitHub Terms of Service §D.5](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service#5-license-grant-to-other-users)

## 对本仓库的可执行选择

在没有指定适用法域和个别权利事实的前提下，工程上可以准备两种方案，但不能替用户作出
法律身份决定：

- **清晰归属方案（稳妥默认）：** `LICENSE`/版权声明和 `CITATION.cff` 使用个人法定姓名；
  GitHub 展示、提交和日常沟通仍使用昵称与 `noreply`；安全问题走 GitHub 私密报告。
- **隐私优先方案：** 所有公开材料只使用稳定昵称/alias，私人保存真实身份、创作记录与权利
  证据；在发布前确认这种署名方式在适用法域及未来维权、商业合作场景是否足够。

无论选择哪一种，项目都必须先选定 OSI 批准的许可证并通过既定发布门禁；单纯把仓库设置
为 public 不是开源发布完成的证据。
