# 文档URL迁移指南

本文档记录了文档结构重构的URL变更。

---

## URL变更表

| 旧URL | 新URL | 说明 |
|---|---|---|
| `docs/guides/randomization.md` | `docs/reference/randomization.md` | 移动到技术参考 |
| `docs/guides/coverage/systemverilog-migration.md` | `docs/reference/coverage/migration.md` | 拆分为概念+场景+参考 |
| `docs/guides/coverage/` | `docs/scenarios/02-collect-coverage.md` | 快速上手 |
| `docs/guides/migration-v0.3.md` | `docs/development/migration/migration-v0.3.md` | 移动到开发文档 |
| `docs/guides/sv-to-python-guide.md` | `docs/reference/sv-converter.md` | 移动到技术参考 |
| `docs/guides/rgm/SSH_ADAPTER_GUIDE.md` | `docs/reference/rgm/SSH_ADAPTER_GUIDE.md` | 移动到技术参考 |

---

## 新文档结构

```
旧结构:
guides/
├── randomization.md
├── coverage/
│   ├── systemverilog-migration.md
│   └── README.md
└── rgm/
    └── SSH_ADAPTER_GUIDE.md

新结构:
scenarios/          # 场景化文档（快速上手）
concepts/           # 概念参考（深入理解）
reference/          # 技术参考（完整API）
├── coverage/
└── rgm/
development/        # 开发文档
└── migration/
```

---

## 重定向规则

所有旧链接已更新到新位置。如果您有外部链接指向旧URL，请更新为新URL。

---

## 迁移原因

1. **更清晰的用户路径** - 场景文档帮助用户快速解决问题
2. **更好的组织** - 概念、场景、参考三层清晰定位
3. **提升可发现性** - 按"我想做什么"而非功能模块组织

---

## 相关信息

- [场景索引](docs/scenarios/)
- [概念索引](docs/concepts/)
- [技术参考索引](docs/reference/)
