# 功能清单

**版本**: v0.2.0

---

## v0.2.0 功能清单

### 1. 随机化与约束系统 ✅

#### 1.1 随机变量

| 功能 | 说明 | 示例 |
|:---|:---|:---|
| **rand变量** | 标准随机变量，每次独立生成 | `@rand def addr(self): return 0` |
| **randc变量** | 循环随机，遍历所有值后重复 | `@randc(bit_width=4) def id(self): return 0` |
| **变量类型** | INT, BIT, ENUM | `RandVar('name', VarType.INT, 0, 100)` |

#### 1.2 约束类型

| 约束类型 | 说明 | 示例 |
|:---|:---|:---|
| **关系运算** | ==, !=, <, >, <=, >= | `"x > 10"` 或 `VarProxy("x") > 10` |
| **逻辑运算** | &&, \|\|, ! | `"a && b"` 或 `a.and(b)` |
| **蕴含运算** | -> (implies) | `"a -> b"` 或 `a.implies(b)` |
| **inside约束** | 范围/值成员 | `"x in [0:100]"` 或 `x inside {[0:100]}` |
| **dist约束** | 权重分布 | `value dist {0:=40, [1:10]:=60}` |
| **算术运算** | +, -, *, /, % | `"a + b"` |
| **位运算** | &, \|, ^, ~, <<, >> | `"a & b"` |

**字符串约束表达式** (新特性 v0.2.0):
- 支持类似SystemVerilog的字符串语法
- 使用`@constraint("name", "expr")`定义
- 更简洁、更接近SystemVerilog风格

```python
# 字符串表达式（推荐）
@constraint("valid_addr", "src_addr >= 0x1000 && src_addr != dest_addr")
def valid_addr_c(self): pass

# 传统表达式（仍支持）
@constraint("valid_addr")
def valid_addr_c(self):
    return VarProxy("src_addr") >= 0x1000 and VarProxy("src_addr") != VarProxy("dest_addr")
```

#### 1.3 求解器

| 求解器 | 特点 | 适用场景 |
|:---|:---|:---|
| **PurePython** | 零依赖，速度快 | 简单约束 (<10变量) |
| **Z3 SMT** | 工业级，可满足性强 | 复杂约束 (>10变量) |

#### 1.4 种子管理

| 类型 | 方法 | 说明 |
|:---|:---|:---|
| **全局种子** | `set_global_seed(42)` | 影响所有新对象 |
| **对象种子** | `Packet(seed=123)` | 影响特定对象 |
| **临时种子** | `pkt.randomize(seed=456)` | 不影响对象状态 |

---

### 2. 功能覆盖率系统 ✅ (v0.2.0)

#### 2.1 核心概念

| 概念 | 说明 | Python实现 |
|:---|:---|:---|
| **CoverGroup** | 覆盖率组 | `CoverGroup("name")` 或 `@covergroup` |
| **CoverPoint** | 覆盖点 | `CoverPoint("name", expr)` 或 `@coverpoint` |
| **Bin** | 覆盖率箱 | 6种类型 |
| **Cross** | 交叉覆盖 | `Cross("name", ["cp1", "cp2"])` |

#### 2.2 Bin类型

| Bin类型 | SystemVerilog语法 | Python参数 | 说明 |
|:---|:---|:---|:---|
| **ValueBin** | `bins b = {1,2,3};` | `"values": [1,2,3]` | 精确值匹配 |
| **RangeBin** | `bins b[] = {[0:255]};` | `"ranges": [[0,255]]` | 范围匹配 |
| **WildcardBin** | `wildcard bins b[] = {8???};` | `"wildcards": ["8???"]` | 通配符匹配 |
| **AutoBin** | `auto_bin_max = 16` | `"auto": 16` | 自动分箱 |
| **IgnoreBin** | `ignore_bins b = {0};` | `"ignore": [0]` | 忽略值 |
| **IllegalBin** | `illegal_bins b = {255};` | `"illegal": [255]` | 非法值 |

#### 2.3 覆盖率采样

| 特性 | 说明 |
|:---|:---|
| **自动采样** | 与Randomizable集成，randomize()时自动采样 |
| **手动采样** | `cg.sample(**kwargs)` |
| **启用/禁用** | `cg.enable_sampling()`, `cg.disable_sampling()` |
| **回调机制** | `pre_sample()`, `post_sample()` |

#### 2.4 报告生成

| 格式 | 特点 | 用途 |
|:---|:---|:---|
| **HTML** | 可视化、交互式 | 人工查看 |
| **JSON** | 机器可读 | CI/CD集成 |
| **UCIS** | IEEE 1687标准 | EDA工具互操作 |

#### 2.5 数据库后端

| 后端 | 特点 | 适用场景 |
|:---|:---|:---|
| **Memory** | 快速访问 | 单次测试运行 |
| **File** | JSON持久化 | 跨会话累积 |

#### 2.6 性能指标

| 指标 | 数值 | 说明 |
|:---|:---|:---|
| 简单采样 | ~246K次/秒 | <10 bins |
| 复杂采样 | ~84.5K次/秒 | >100 bins |
| 目标要求 | >10K/1K次/秒 | 远超要求 |

---

### 3. 回归测试Agent ✅

#### 3.1 核心功能

- 自动代码变更检测
- 智能影响分析
- 自动测试选择与运行
- 详细测试报告

---

## 规划中的功能 (v0.3.0+)

### 寄存器模型系统 📋 (v0.3.0)

- 层次化组织 (RegisterBlock → Register → Field)
- 访问控制 (RW, RO, WO, W1C, W1S)
- 前门/后门访问
- 代码生成 (Verilog RTL, C头文件, Python包装器)

### 覆盖率引导随机化 📋 (v0.4.0)

- 智能约束求解
- 自动达到目标覆盖率
- 覆盖率驱动验证

### DUT配置转换 📋 (v0.5.0)

- Verilog/SystemVerilog解析
- Python模型自动生成
- 测试框架自动生成

---

## 版本历史

详见 [CHANGELOG.md](../../CHANGELOG.md)

---

## 相关文档

- 📖 [随机化系统指南](../guides/randomization.md)
- 📊 [覆盖率系统指南](../guides/coverage/)
- 🎯 [应用场景](use-cases.md)
- 🔄 [与UVM对比](comparison.md)
