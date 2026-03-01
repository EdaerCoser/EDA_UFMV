# 文档维护指南

## 版本
v1.0 - 2026-03-01

---

## 目录结构规范

```
docs/
├── README.md                    # 文档导航中心
│
├── product/                     # 产品文档
│   ├── overview.md             # 产品概述
│   ├── features.md             # 功能列表
│   ├── use-cases.md            # 应用场景
│   ├── comparison.md           # 竞品对比
│   └── RGM_GUIDE.md            # RGM完整用户指南
│
├── guides/                      # 使用指南
│   ├── README.md               # 指南导航
│   ├── randomization.md        # 随机化系统指南
│   ├── constraints.md          # 约束系统指南
│   ├── seeding.md              # 种子管理指南
│   ├── coverage/               # 覆盖率指南
│   │   ├── README.md           # 覆盖率概述
│   │   ├── api-reference.md    # API参考
│   │   └── systemverilog-migration.md  # SV迁移指南
│   └── rgm/                    # RGM指南
│       ├── README.md           # RGM概述
│       └── SSH_ADAPTER_GUIDE.md # SSH适配器指南
│
├── user/                        # 用户文档
│   └── README.md               # 快速开始指南
│
├── development/                 # 开发文档
│   ├── ROADMAP.md              # 开发路线图
│   ├── ARCHITECTURE.md         # 架构设计
│   ├── CONTRIBUTING.md         # 贡献指南
│   ├── TEST_AGENT_GUIDE.md     # 测试代理指南
│   └── DOCUMENTATION_GUIDELINES.md  # 本文档
│
└── legacy/                      # 废弃文档（保留用于历史参考）
    └── [已归档文件]
```

---

## 文档生命周期管理

### 1. 活跃文档
**位置**: `docs/product/`, `docs/guides/`, `docs/user/`, `docs/development/`

这些文档与当前版本保持同步：
- 必须准确反映当前代码状态
- 每次功能更新时同步更新
- 版本号与代码版本一致

### 2. 历史文档
**位置**: `docs/development/history/` 或 `docs/legacy/`

这些文档记录历史变更：
- 不再与当前代码同步
- 保留用于理解设计演进
- 添加日期标记和版本信息

### 3. 废弃文档
**位置**: `docs/legacy/` (已归档)

这些文档已过时：
- 内容已被新文档替代
- 保留用于历史参考
- 在文件头部添加弃用说明

---

## 文档命名规范

### 标准命名
- 使用大写 snake_case: `FEATURE_GUIDE.md`
- 使用描述性名称: `API_REFERENCE.md` 而非 `API.md`
- 概述文档使用: `README.md`

### 特殊前缀
- **开发中**: `DRAFT_` 前缀
- **过时**: `DEPRECATED_` 前缀
- **草稿**: `DRAFT_` 前缀

---

## 文档内容规范

### 1. Markdown 头部元数据

每个文档应包含以下元数据：

```markdown
# 文档标题

**版本**: vX.X.X
**状态**: Stable/Draft/Deprecated
**更新日期**: YYYY-MM-DD
**维护者**: 负责人/团队

---

## 概述
[简要描述文档内容和目标读者]
```

### 2. 内容结构

```markdown
## 目录

1. [章节1](#章节1)
2. [章节2](#章节2)
...

---

## 章节1

### 子章节
- 要点1
- 要点2

---

## 章节2
[内容]
```

### 3. 代码示例规范

- 使用语法高亮: \```python
- 添加注释解释关键步骤
- 提供完整可运行的示例
- 标注示例文件路径

```python
# 示例：创建RegisterBlock
from rgm import RegisterBlock, Register, Field, AccessType

# 创建寄存器块
uart = RegisterBlock("UART", base_address=0x40000000)

# 添加寄存器
ctrl = Register("CTRL", 0x00, 32)
ctrl.add_field(Field("enable", 0, 1, AccessType.RW, 1))
uart.add_register(ctrl)
```

---

## 文档维护规则

### 1. 何时更新文档

**必须更新**:
- 新增功能时
- API 变更时
- 行为变化时
- 发现错误时

**建议更新**:
- 改进示例代码
- 添加更多用例
- 优化说明清晰度

### 2. 文档审查流程

1. **作者创建/修改** → 确保内容准确
2. **自我审查** → 检查格式、链接、代码示例
3. **PR审查** → 其他开发者审查
4. **合并** → 更新文档索引

### 3. 文档测试

- 所有代码示例必须可运行
- 所有链接必须有效
- 所有引用文件必须存在

---

## 冗余文件处理

### 识别冗余

重复或冗余文档的判断标准：
1. **内容重复**: 两份文档描述相同内容
2. **信息过时**: 文档描述已被新版本替代
3. **位置错误**: 文档放在错误的目录中
4. **用途不明**: 文档用途不清晰或已失效

### 处理方式

| 情况 | 处理方式 |
|:---|:---|
| 内容完全重复 | 删除较旧/较短的版本 |
| 部分重复 | 合并到主文档，添加链接 |
| 已有替代文档 | 移至 `legacy/` 并添加说明 |
| 过时但有价值 | 移至 `development/history/` |
| 完全无用 | 删除 |

### 当前冗余文件清单

#### 建议移至 legacy/

以下文档已被新版本替代，移至 `docs/legacy/` 保留历史参考：

| 文件 | 替代文档 | 原因 |
|:---|:---|:---|
| `docs/legacy/ARCHITECTURE.md` | `docs/development/ARCHITECTURE.md` | 旧版架构文档 |
| `docs/legacy/IMPLEMENTATION_PLAN.md` | `docs/development/ROADMAP.md` | 实施计划已被路线图替代 |
| `docs/legacy/SEED_CONTROL.md` | `docs/guides/seeding.md` | 功能已整合到用户指南 |

#### 建议移至 development/history/

| 文件 | 原因 |
|:---|:---|
| `docs/development/history/CLEANUP_SUMMARY.md` | 记录项目清理历史 |
| `docs/development/history/REFACTORING_SUMMARY.md` | 记录重构历史 |

#### 建议删除

| 文件/目录 | 原因 |
|:---|:---|
| `docs/api/` (空目录) | 空目录，无内容 |
| `docs/user/README.md` | 内容与 `docs/README.md` 重复 |

---

## 文档质量检查清单

在提交文档更新前，请确认：

- [ ] 文件头部包含版本、状态、日期
- [ ] 所有代码示例可运行
- [ ] 所有内部链接有效
- [ ] 所有外部链接可访问
- [ ] 遵循 Markdown 格式规范
- [ ] 拼写和语法正确
- [ ] 技术内容准确
- [ ] 示例清晰易懂
- [ ] 已更新相关索引文件
- [ ] 已更新 CHANGELOG.md（如适用）

---

## 文档索引维护

### 主索引 (docs/README.md)

必须保持以下部分最新：
- 产品文档链接
- 用户指南链接
- 开发文档链接
- 快速链接

### 二级索引

各目录的 README.md 必须维护：
- 该目录的文档列表
- 文档用途说明
- 推荐阅读顺序

---

## 自动化检查

建议添加的 CI 检查：

1. **Markdown Linting**:
   ```yaml
   - name: Lint Markdown files
     uses: actionshub/markdownlint@v3.1.2
   ```

2. **链接检查**:
   ```bash
   # 检查文档中的死链接
   find docs -name "*.md" -exec markdown-link-check {} \;
   ```

3. **示例代码测试**:
   ```bash
   # 提取并测试文档中的代码块
   python tools/test_doc_examples.py
   ```

---

## 文档版本控制

### 版本策略

- **主版本**: 文档结构重大变更
- **次版本**: 新增章节或重要内容
- **修订版本**: 小修改、错误修复

### 变更日志

在文档底部添加变更记录：

```markdown
---

## 变更日志

| 版本 | 日期 | 变更内容 | 作者 |
|:---|:---|:---|:---|
| v1.1 | 2026-03-01 | 添加装饰器API章节 | XXX |
| v1.0 | 2026-02-15 | 初始版本 | XXX |
```

---

## 贡献指南

### 如何贡献文档

1. 确定文档类型和位置
2. 遵循本文档规范
3. 提交 Pull Request
4. 等待审查和合并

### 文档模板

新建文档时，使用以下模板：

```markdown
# 文档标题

**版本**: v0.1.0
**状态**: Draft
**更新日期**: YYYY-MM-DD

---

## 概述
[描述文档目的和目标读者]

## 目录
1. [章节1](#章节1)
2. [章节2](#章节2)

---

## 章节1
[内容]

---

## 变更日志

| 版本 | 日期 | 变更内容 | 作者 |
|:---|:---|:---|:---|
| v0.1 | YYYY-MM-DD | 初始版本 | Your Name |
```

---

## 总结

遵循本文档指南可以确保：

1. **一致性**: 所有文档遵循相同的结构和风格
2. **可维护性**: 清晰的生命周期管理
3. **可发现性**: 良好的组织和索引
4. **高质量**: 明确的质量标准和检查清单

记住：**好的文档是项目成功的关键**。
