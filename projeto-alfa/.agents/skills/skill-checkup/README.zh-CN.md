[English](README.md) | 简体中文

<div align="center">

# skill-checkup

**帮你把 skill 的内容放对地方:该拆的拆,用到才读,上下文只装当下需要的。**

![Claude Skill](https://img.shields.io/badge/Claude-Skill-8A2BE2)
![确定性检查](https://img.shields.io/badge/checks-4%20deterministic-2ea44f)
![引用文件](https://img.shields.io/badge/references-20%20on--demand-blue)
![运行依赖](https://img.shields.io/badge/runtime%20deps-none-success)
![Python](https://img.shields.io/badge/python-3-3776AB)

一个审别的 skill 的 skill。机器能定的事——字符数、断链、清单预算——交给脚本和退出码定;需要判断的事——没用的指令、臃肿、模糊到没法执行的收尾条件——才留给人看。它报出的每个毛病都带名字和行号。

[看它跑一遍](#看它跑一遍) · [快速上手](#快速上手) · [它能逮住什么](#它能逮住什么) · [它凭什么不一样](#它凭什么不一样) · [怎么运作](#怎么运作) · [速查](#速查)

</div>

---

## 看它跑一遍

一份真实诊断,略作精简:

```text
$ "审查我的 image-tool skill"

[skill-checkup] Auditing: ~/.claude/skills/image-tool  body=143 lines  description=52 chars
[skill-checkup] Budget: 32 skills installed, 11,515 chars vs ≈40,000 → fits
[skill-checkup] Dry-run prompt: "use image-tool to convert this"  broken links=1

[skill-checkup] Diagnosis

❌ Must fix (P0→P3)
  [P0 effect break]  Step 3 读 "the output file",但 Step 2 从没命名过输出
                     → 让 Step 2 写一个有名字的产物,Step 3 才接得住
  [P1 structure]     description 用了第一人称("I help you resize…")
                     → 改成第三人称("Resizes and converts images…")
  [P2 specificity]   "process the image" 没有命令
                     → "convert to PNG with `sips -s format png`"

⚠️ Suggested
  - [no-op] "be careful and thorough"——模型本来就会 → 删掉这行
  - [sprawl] body 143 行;一段 40 行的示例 → 挪进 references/

✅ Passed
  - name 规则、路由(0 orphan / 0 dangling)、YAML、每步有可见输出
```

坏掉的 skill 有个特点:**它不报错**。它只是不触发,或者 Claude 读了一半就悄悄走开。你几周后才发现,自己写的 skill 一次都没被叫起来过。skill-checkup 就是上线前逮住这件事的那一道关。

---

## 快速上手

在 Claude 会话里,对着任何一个 skill 直接说:

```
审查 / 体检 / 修复 这个 skill   ·   review this skill   ·   "检查 my-tool"
```

或者绕开 Claude,直接在终端跑某一项确定性检查:

```bash
python3 scripts/check_routes.py ~/.claude/skills/my-tool
# exit 0 = 干净 · exit 1 = 有 orphan / 断链 / 超出体积上限
```

它会读目标、跑机械检查、把一条真实 prompt 在流程里走一遍,然后打出 P0→P3 报告。**你不说"改",它绝不动你的文件。**

---

## 它能逮住什么

那些不会自己喊出来的故障:

| 你根本不会注意到的症状 | 它会标出 |
| :--- | :--- |
| skill 从不自动触发 | description 用第一人称、太弱、或超出清单预算(被悄悄降成只剩名字) |
| Claude 跳过你一半的指令 | body 超过约 500 行——`[sprawl]` |
| 某个 reference 文件从没被读到 | orphan 或断链,`check_routes.py` 抓出来 |
| 某个流程步骤被跳过 | 这步没有可见输出,模型就走过去了 |
| agent 提前结束某一步 | 收尾条件太模糊——`[premature-completion]` |
| 一行什么都没做的指令 | 模型默认本来就会——`[no-op]` |

每一项检查、阈值、规则,下面[速查](#速查)里全列了。

---

## 它凭什么不一样

一个正经的 skill 是一堆文件:主文件(SKILL.md)+ 细则文件夹(references/)+ 脚本(scripts/)。它管的是内容怎么摆:主文件只放路线,细则拆出去、标清什么时候读哪份,Claude 用到哪份才读哪份——上下文不会被一口气塞爆。摆得不合理,代价全是无声的:几千字全堆在主文件里,每次全量占上下文;某份细则永远没被读过;链接指着不存在的文件。全都不报错,你不会发现。市面上的工具只查单个文件的格式,内容怎么摆这件事基本没人管。

1. **按整套查,不按单个文件查。** 主文件、它背后的每份细则、附带的每个脚本,是同一个检查对象。哪个文件永远轮不到被读、哪条链接指向了不存在的东西、哪个文件超了上限,都是头等问题。
2. **"找不找得到"是测出来的,不是猜的。** 每份细则都标着"什么时候该读我",工具会实际测一遍:凭这句话,真能把这份文件找回来吗?从主文件出发最多允许跳两次,超了就报。
3. **细则按"跳过它会怎样"分成三类。** 有的查表用,跳过无妨;有的是清单,漏一条就是无声的错;有的必须通读吸收。判断标准一句话:跳过这个文件,出的错是不是无声的?三类各配不同的强制手段。
4. **拆文件有规矩。** 把内容从一个文件挪进另一个文件,只许原样搬运,不许顺手改写;搬完自动核对字没少、没变;随时能退回去。
5. **装着几百个素材文件的 skill,有专门的结构方案。** 三层目录:索引 → 卡片 → 素材本体,在装着 187 个和 112 个真实文件的两个库上验证过。
6. **小 skill 小查,大 skill 大查。** 脚本先把目标量一遍,再决定哪些检查项要跑;目标太大就拆给几个 agent 分头查。5 行的小 skill 和 90KB 的大库,同样认真,花的力气不一样。

查格式的工具和它不冲突:单个文件的卫生交给那些工具,文件之间的结构交给它。

---

## 怎么运作

```text
  你的 skill  (SKILL.md + references/ + scripts/)
        |
        v
  机械检查 ............ 字符 / 行数 · 清单预算
  (脚本,带退出码)       路由可达性 · 召回评测
        |
        v
  判断 ................ 臃肿 · no-op · sediment · 模糊收尾
  (维度,按需加载)       只在条件命中时才读
        |
        v
  Dry-run ............ 把一条真实 prompt 在流程里走一遍
        |
        v
  P0 -> P3 报告 ...... 必修 / 建议 / 通过,每条带行号
        |
        v
  应用修复 ........... 只在你确认后
```

两个设计让它的结论值得信:

- **能确定的就确定。** 字符数、路由、预算,由带退出码的脚本定,不靠每次都会飘的主观判断。
- **不能确定的就诚实。** 如果 skill-checkup 在同一个会话里已经改过你的 skill,它会给报告每一行盖上 `[self-review]`,并提醒你换一个全新 agent 复核。它**故意给自己的结论打折**。

<!-- ============ 速查区——查东西时再看,平时可跳过 ============ -->

---

## 速查

下面全是查阅资料,用这个 skill 不需要读它。

### 诊断流程

| 步骤 | 做什么 | 输出 |
| :--- | :--- | :--- |
| 1 | 读目标 SKILL.md;跑 `check_listing_budget.py`、`check_routes.py` 和 `check_script_safety.py` | 体积 + 预算 + 路由 + 安全四条结论 |
| 2 | `index.py` 测量目标,给每个维度点名(FORCED / DEFAULT / SKIP,外加一行 `MODE=` 派发);命中的逐个文件读 | 点名清单 + 每个维度一行回执 |
| 2.5 | Dry-run:每种任务形状(写 / 改 / 查 / 重构)各拿一条 prompt 在 body 里走一遍 | 每条 prompt 的断链数与触发的门(有断链就 P0) |
| 2.6 | Live-injection:本会话目标的 description 是真注入了,还是被降成只剩名字 | injected / dropped / skipped |
| 3 | 打出 P0→P3 诊断(❌ 必修 · ⚠️ 建议 · ✅ 通过) | 报告 |
| 4 | 用 Edit 应用修复——只在你确认后 | 已修复行数 |

### 自带脚本

无 LLM、无第三方依赖(`eval_retrieval.py --glm` 和 `glm_blind_audit.py` 除外,它们按需调模型)。

| 脚本 | 检查什么 | 命令 | 退出码 |
| :--- | :--- | :--- | :--- |
| `index.py` | 测量目标,打印维度点名(FORCED / DEFAULT / SKIP 带理由)和 `MODE=` 派发行 | `python3 scripts/index.py <skill_dir>` | 0 已点名 / 2 读不了 |
| `check_routes.py` | 可达性、orphan、断链、compass 上限(默认 6000 字符,可用 frontmatter 的 `compass-cap:` 覆写);`--before <snapshot>` 加一道内容守恒检查 | `python3 scripts/check_routes.py <skill_dir>` | 0 干净 / 1 有问题 / 2 不可用 |
| `check_script_safety.py` | 扫自带脚本和 prose 里的风险模式(外传、破坏性操作、持久化);检测是机械的,定罪归审计者 | `python3 scripts/check_script_safety.py <skill_dir>` | 0 已扫(命中算发现) / 2 不可用 |
| `check_listing_budget.py` | description 总字符 vs 约占 1% 上下文的清单池;列出每个超 300 字符带的 description | `python3 scripts/check_listing_budget.py <root>` | 0 装得下 / 1 超出 / 2 不可用 |
| `check_desc_slim.py` | 标出能瘦身、又不丢触发力的 description | `python3 scripts/check_desc_slim.py <skill_dir>` | 0 干净 / 1 有问题 |
| `eval_retrieval.py` | 问模型(GLM,3 次多数投票)路由能不能凭 `when-to-read` 场景找到每个 reference | `python3 scripts/eval_retrieval.py <skill_dir> --glm` | 0 干净 / 1 有漏 |
| `glm_blind_audit.py` | 把整个包打包进一次跨模型(GLM)调用,拿一份独立盲审第二意见 | `python3 scripts/glm_blind_audit.py <skill_dir>` | 0 意见已打印 / 2 无 key 或断网 |

### 硬规则

这里违反一条就是错,不是建议。

| 规则 | 出处 |
| :--- | :--- |
| description ≤ 1024 字符(Claude Code ≥ 2.1.105 收到 1536) | Anthropic spec / CC release notes |
| 清单预算超标一律上报——这是全局事实,靠全局瘦身解决,绝不靠改单个 skill | CC issues #56710 / #47627 |
| description 用第三人称 | Anthropic best practices |
| name 只用小写字母、数字、连字符 | Anthropic spec |
| body < 500 行 | Anthropic / 社区共识 |
| 路由深度 ≤ 2 跳(SKILL.md → index.md → 文件);禁止嵌套索引 | structure-surgery(实践中加硬) |
| 零断链、零 orphan 子文档 | structure-surgery 铁律 |
| description 写在单一逻辑 YAML 行(不用 `>` 或 `|`) | Prettier 重排会弄坏 |
| 多步流程每一步都要有可见输出 | Seleznov 实验 |
| skill 对自己性能的声明必须指向仓库内证据,否则删掉 | evidence-gating |

### 它会命名的失效模式

毛病有名字才好下手:P 级说**有多严重**,名字说**是哪一类**。

- `[no-op]` —— 模型默认本来就会做的一行
- `[sediment]` —— 漂出相关性的陈旧行
- `[sprawl]` —— 单纯太长,哪怕每行都还有用
- `[duplication]` —— 同一个意思出现在不止一处
- `[premature-completion]` —— 收尾条件模糊到 agent 提前收工
- `[weak-leading-word]` —— 锚点词太弱,压不过模型默认
- `[no-floor]` —— 没规定必读文件集,每次审的深度都不一样
- `[gate-gap]` —— 质量门全绑在大任务上,日常小改一道门也不过
- `[missing-license]` —— 改写类 skill 没写明改写授权,模型只敢做最小改动

### 优先级分级

| 级别 | 含义 | 进 ❌ |
| :--- | :--- | :--- |
| **P0** | 效果断裂(跑起来流程接不上) | 总是 |
| **P1** | 违反结构硬规则 | 总是 |
| **P2** | 不够具体(没命令、没 I/O 规格) | 总是 |
| **P3** | 可读性 | 只有当它改变下一次运行的结果时;否则进 ⚠️ |

### 维度(由 `scripts/index.py` 点名加载)

`scripts/index.py` 决定哪些维度文件要读(FORCED / DEFAULT / SKIP);流程文档由点名它的步骤拉取。`references/index.md` 是给人看的镜像。

| Reference | 管什么 |
| :--- | :--- |
| `description-templates.md` | 触发强度模板 + 路由区分度 |
| `slimming-workflow.md` | 全局瘦身操作:预算上限、压缩顺序、安全协议 |
| `catalog-skill-pattern.md` | 大批量载荷 skill 的三层目录结构 |
| `body-quality-checklist.md` | body 体积、什么该挪进 references |
| `visible-output-rule.md` | 每个流程步骤都得有输出 |
| `yaml-pitfalls.md` | frontmatter 格式坑 |
| `hard-code-vs-llm-judgment.md` | 该写成脚本,还是留给模型 |
| `assets-vs-references.md` | 模板 vs reference 文档怎么分 |
| `structure-surgery.md` | 拆分、路由分层、2 跳上限 |
| `effect-dry-run.md` | 每种任务形状各走一条 prompt |
| `runtime-contract.md` | 必读下限、门槛粒度、改写授权:防"触发了但改得浅" |
| `priority-tiers.md` | P0–P3 定义与归类 |
| `predictability-glossary.md` | 失效模式词汇表 |
| `hard-rules.md` | 量化的必过规则 |
| `exception-fallback.md` | 路径或脚本出错时怎么办 |
| `language-policy.md` | 默认英文及其例外 |
| `output-format.md` | Step 3 报告的分层版式 |
| `apply-safety.md` | 体积闸、删除前检查、闭环收尾 |
| `live-injection-check.md` | 本会话 description 是否真被注入 |
| `rationale.md` | 这个 skill 为什么存在 |

### 仓库结构

```text
skill-checkup/
├── SKILL.md                              # compass:诊断流程 + 路由
├── references/
│   ├── index.md                          # 按 when-to-read 路由到每个维度
│   ├── apply-safety.md
│   ├── assets-vs-references.md
│   ├── body-quality-checklist.md
│   ├── catalog-skill-pattern.md
│   ├── description-templates.md
│   ├── effect-dry-run.md
│   ├── exception-fallback.md
│   ├── hard-code-vs-llm-judgment.md
│   ├── hard-rules.md
│   ├── language-policy.md
│   ├── live-injection-check.md
│   ├── output-format.md
│   ├── predictability-glossary.md
│   ├── priority-tiers.md
│   ├── rationale.md
│   ├── runtime-contract.md
│   ├── slimming-workflow.md
│   ├── structure-surgery.md
│   ├── visible-output-rule.md
│   └── yaml-pitfalls.md
├── scripts/
│   ├── index.py                          # 维度点名:FORCED / DEFAULT / SKIP + MODE=
│   ├── check_routes.py                   # 可达性 / orphan / 断链 / compass 上限
│   ├── check_listing_budget.py           # description 清单预算
│   ├── check_desc_slim.py                # description 瘦身
│   ├── check_script_safety.py            # 自带脚本风险模式扫描
│   ├── eval_retrieval.py                 # 召回评测(调模型)
│   └── glm_blind_audit.py                # 跨模型盲审第二意见
├── README.md
├── README.zh-CN.md
└── LICENSE
```

---

<div align="center">

*skill 总是悄无声息地坏掉。这是让它先大声坏给你看的那道关。*

**作者:** [Zane456](https://github.com/Zane456) · **License:** [MIT](LICENSE)

</div>
