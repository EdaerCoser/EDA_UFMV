# EDA_UFMV 开发路线图

**文档版本**: v1.0
**最后更新**: 2026年3月1日
**项目地址**: https://github.com/EdaerCoser/EDA_UFMV

---

## 版本规划概览

EDA_UFMV采用分阶段迭代开发策略，每个版本都有明确的功能目标和里程碑。

```
v0.1.0 ────► v0.2.0 ────► v0.3.0 ────► v0.4.0 ────► v0.5.0 ────► v1.0.0
 (已完成)   (覆盖率)   (RGM)      (增强)     (解析)    (完整版)
 2026-02     2026 Q2    2026 Q3    2026 Q3    2026 Q4    2027 Q1
```

---

## v0.1.0 - 基础随机化框架 ✅

**状态**: 已完成
**发布时间**: 2026年2月
**代码提交**: 558dca6

### 核心功能

- ✅ 随机变量系统（rand/randc）
- ✅ 约束系统（inside, dist, 表达式）
- ✅ 双求解器架构（PurePython + Z3）
- ✅ 种子管理系统
- ✅ 回归测试Agent
- ✅ 36个单元测试（全部通过）

### 技术亮点

- 完整的表达式AST系统
- 支持SystemVerilog风格的约束语法
- 可插拔求解器架构
- 覆盖率引导的随机化基础

### 代码统计

- **文件数**: 43个
- **代码行数**: 8220行
- **测试覆盖率**: 36个单元测试
- **文档**: 3个技术文档

---

## v0.2.0 - 功能覆盖率系统 📋

**预计时间**: 2026年Q2（4-6周）
**优先级**: 高

### 目标功能

实现类似SystemVerilog的功能覆盖率系统，支持covergroup/coverpoint/cross覆盖。

### 核心模块

**1. CoverGroup实现**
```python
class CoverGroup:
    def __init__(self, name: str):
        self.name = name
        self._coverpoints = {}
        self._crosses = {}

    def coverpoint(self, name: str, **kwargs):
        """装饰器：定义覆盖点"""
        pass

    def cross(self, name: str, *coverpoints):
        """定义交叉覆盖"""
        pass
```

**2. CoverPoint实现**
```python
class CoverPoint:
    def __init__(self, name: str, sample_func, bins, auto_bin_max=None):
        self.name = name
        self._bins = {}  # bins定义
        self._hit_count = {}  # 命中计数

    def sample(self):
        """采样当前值"""
        pass

    def get_coverage(self) -> float:
        """计算覆盖率百分比"""
        pass
```

**3. Bin类型**
- value_bin: 单个值
- range_bin: 值范围 [low:high]
- wildcard_bin: 通配符匹配
- auto_bin: 自动分箱
- ignore_bin: 忽略的值
- illegal_bin: 非法值

**4. 覆盖率报告**
- HTML格式
- UCIS格式（UCIS标准）
- JSON格式（用于CI/CD）

### 里程碑

- **M1** (2周): CoverGroup基础类 + CoverPoint实现
- **M2** (2周): Bin系统 + 采样引擎
- **M3** (2周): Cross覆盖 + 报告生成器

### 技术风险

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 覆盖率数据库性能 | 中 | 增量更新、数据库持久化 |
| 大规模bin管理 | 中 | 分页加载、懒加载 |
| 报告生成速度 | 低 | 模板优化、增量生成 |

### 交付物

- `sv_randomizer/coverage/` 模块
- `examples/coverage/` 示例代码
- `tests/test_coverage/` 单元测试
- `docs/product/COVERAGE_GUIDE.md` 用户指南

---

## v0.3.0 - 寄存器模型系统 ✅

**状态**: 已完成
**发布时间**: 2026年3月
**代码提交**: (待定)

### 核心功能

- ✅ Field类（15种AccessType，UVM风格接口）
- ✅ Register类（set/get/update/mirror/poke/peek）
- ✅ RegisterBlock类（层次化组织）
- ✅ RegisterMap类（UVM地址映射）
- ✅ FrontDoor/BackDoor访问接口
- ✅ 硬件适配器（AXI/APB/UART/SSH）
- ✅ 代码生成器（Verilog/C/Python）
- ✅ 186+单元测试通过

### 技术亮点

- 完整的UVM RGM兼容接口
- 支持15种访问类型（RW, RO, WO, W1C, W1S, W0C, W0S, RC, RS, WC, WS等）
- SSH远程单板访问支持
- 工厂模式的代码生成器
- 213个测试用例，186个通过

### 代码统计

- **文件数**: 25个核心文件
- **代码行数**: ~3500行
- **测试覆盖率**: 213个测试，186个通过

### 核心模块

**1. Field类**
```python
class Field:
    def __init__(self, name, bit_width, access='RW', reset_value=0):
        self.name = name
        self.bit_width = bit_width
        self.access = access  # RW, RO, WO, W1C, W1S, etc.
        self.reset_value = reset_value

    def read(self) -> int:
        """读取字段值"""
        pass

    def write(self, value: int) -> None:
        """写字段值"""
        pass
```

**2. Register类**
```python
class Register:
    def __init__(self, name, offset, width=32):
        self.name = name
        self.offset = offset
        self.width = width
        self._fields = {}

    def add_field(self, field: Field, bit_offset: int):
        """添加字段"""
        pass

    def read(self) -> int:
        """读取寄存器值"""
        pass

    def write(self, value: int):
        """写入寄存器值"""
        pass
```

**3. RegisterBlock类**
```python
class RegisterBlock:
    def __init__(self, name, base_address=0):
        self.name = name
        self.base_address = base_address
        self._registers = {}
        self._blocks = {}
        self._address_map = {}

    def add_register(self, register: Register):
        """添加寄存器"""
        pass

    def add_block(self, block: 'RegisterBlock'):
        """添加子块"""
        pass

    def get_register(self, name: str) -> Register:
        """获取寄存器（支持层次化路径）"""
        pass
```

**4. 访问接口**
```python
class FrontDoorAccess:
    """前门访问（通过总线）"""
    def read(self, address: int) -> int: pass
    def write(self, address: int, value: int): pass

class BackDoorAccess:
    """后门访问（直接读写）"""
    def read(self, address: int) -> int: pass
    def write(self, address: int, value: int): pass
```

**5. 代码生成器**
```python
class VerilogGenerator:
    def generate(self, block: RegisterBlock) -> str:
        """生成Verilog RTL代码"""
        pass

class CHeaderGenerator:
    def generate(self, block: RegisterBlock) -> str:
        """生成C头文件"""
        pass
```

### 里程碑

- **M1** (3周): Field + Register基础类
- **M2** (2周): RegisterBlock层次化
- **M3** (3周): 访问接口 + 代码生成器

### 技术风险

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 并发访问冲突 | 中 | 访问锁、事务性接口 |
| 大型设计内存占用 | 中 | 惰性加载、数据库持久化 |
| 地址映射复杂性 | 低 | 清晰的文档、示例 |

### 交付物

- `sv_randomizer/rgm/` 模块
- `examples/rgm/` 示例代码
- `tests/test_rgm/` 单元测试
- `docs/product/RGM_GUIDE.md` 用户指南

---

## v0.4.0 - 随机化增强 📋

**预计时间**: 2026年Q3（4-6周）
**优先级**: 中

### 目标功能

实现覆盖率引导的智能随机化，自动调整随机策略以最大化覆盖率。

### 核心模块

**1. CoverageGuidedRandomizer**
```python
class CoverageGuidedRandomizer:
    def __init__(self, obj: Randomizable, covergroup: CoverGroup):
        self.obj = obj
        self.covergroup = covergroup
        self._target_coverage = 100.0
        self._max_iterations = 10000

    def randomize_until_coverage(self, target_coverage: float = 100.0) -> bool:
        """随机化直到达到目标覆盖率"""
        pass
```

**2. 覆盖率分析器**
```python
class CoverageAnalyzer:
    def analyze_uncovered_bins(self) -> Dict[str, List[str]]:
        """分析未覆盖的bins"""
        pass

    def suggest_targeted_constraints(self) -> List:
        """建议针对性约束"""
        pass
```

**3. 动态权重调整**
```python
class DynamicWeightAdjuster:
    def adjust_weights(self, uncovered_bins):
        """根据未覆盖bins调整DistConstraint权重"""
        pass
```

### 里程碑

- **M1** (2周): 覆盖率引导框架
- **M2** (2周): 智能约束求解
- **M3** (2周): 性能优化和测试

### 技术风险

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 覆盖率收敛速度 | 中 | 增量分析、采样优化 |
| 求解器选择策略 | 低 | 启发式算法、性能基准 |

### 交付物

- `sv_randomizer/enhanced_randomization/` 模块
- `examples/enhanced_rand/` 示例代码
- `tests/test_enhanced_rand/` 单元测试
- `docs/product/ENHANCED_RAND_GUIDE.md` 用户指南

---

## v0.5.0 - DUT配置转换 📋

**预计时间**: 2026年Q4（8-10周）
**优先级**: 高

### 目标功能

解析Verilog/SystemVerilog DUT定义，自动生成Python验证模型。

### 核心模块

**1. Verilog解析器**
```python
class VerilogParser:
    def parse_file(self, filepath: str) -> Dict[str, Any]:
        """解析Verilog文件"""
        pass

    def _extract_modules(self, content: str):
        """提取模块定义"""
        pass

    def _extract_registers(self, content: str):
        """提取寄存器声明"""
        pass

    def _extract_parameters(self, content: str):
        """提取参数定义"""
        pass
```

**2. SystemVerilog约束解析器**
```python
class SVConstraintParser:
    def parse_constraint_block(self, sv_text: str) -> List:
        """解析约束块"""
        pass

    def to_python_constraint(self, sv_constraint) -> Dict:
        """转换为Python约束"""
        pass
```

**3. Python模型生成器**
```python
class PythonModelGenerator:
    def generate_from_verilog(self, parsed_data: Dict) -> str:
        """从Verilog AST生成Python代码"""
        pass

    def generate_register_block(self, registers: List[Dict]) -> str:
        """生成RegisterBlock代码"""
        pass
```

### 支持的Verilog构造

**第一阶段**（常用子集）:
- 模块定义
- 寄存器声明（logic, reg）
- 参数定义
- 基本约束

**第二阶段**（扩展）:
- 接口定义
- 任务/函数
- 复杂数组
- 类构造

### 里程碑

- **M1** (3周): Verilog词法/语法解析
- **M2** (3周): AST构建和模型生成
- **M3** (2-4周): 约束转换和测试框架

### 技术风险

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| Verilog语法复杂度 | 高 | 渐进式实现、使用PyVerilog库 |
| 解析器性能 | 中 | 惰性求值、AST缓存 |
| 类型映射准确性 | 中 | 严格类型检查、验证测试 |

### 依赖库

- **可选**: PyVerilog（简化Verilog解析）
- **可选**: PyVeristar（SystemVerilog支持）

### 交付物

- `parser/` 模块（与sv_randomizer同级）
- `examples/parser/` 示例代码
- `tests/test_parser/` 单元测试
- `docs/product/PARSER_GUIDE.md` 用户指南

---

## v1.0.0 - 完整平台 📋

**预计时间**: 2027年Q1（4-6周）
**优先级**: 高

### 目标功能

系统集成、性能优化、文档完善，达到生产就绪状态。

### 核心任务

1. **系统集成**
   - 集成所有模块
   - 统一API接口
   - 端到端测试

2. **性能优化**
   - 性能基准测试
   - 瓶颈优化
   - 内存优化

3. **文档完善**
   - API参考手册
   - 完整教程
   - 最佳实践指南

4. **发布准备**
   - PyPI打包发布
   - CI/CD配置
   - 宣传材料

### 里程碑

- **M1** (2周): 系统集成
- **M2** (1周): 性能优化
- **M3** (1周): 文档完善
- **M4** (1周): 发布准备

### 质量目标

- **测试覆盖率**: >90%
- **性能基准**: 比UVM快10倍
- **文档完整性**: 所有API有文档
- **稳定性**: 0个critical bug

### 交付物

- PyPI发布版本
- 完整文档网站
- CI/CD管道
- 发布notes

---

## 依赖关系图

```
v0.1.0 (基础框架)
    ↓
    ↓
v0.2.0 (覆盖率系统) ────────┐
    ↓                           │
v0.3.0 (寄存器模型)            │
    ↓                           │
    └── v0.4.0 (随机化增强) ────┘
        ↓
v0.5.0 (DUT配置转换)
    ↓
v1.0.0 (完整平台)
```

**说明**:
- v0.2.0和v0.3.0可以并行开发（依赖小）
- v0.4.0依赖v0.2.0（需要覆盖率系统）
- v0.5.0可以独立开发
- v1.0.0依赖所有前期版本

---

## 技术债务管理

### 当前技术债务

1. **测试覆盖率**: 需要达到90%+
2. **类型注解**: 需要添加完整的类型提示
3. **文档**: 需要补充API参考手册
4. **性能优化**: 大规模场景需要优化

### 债务清理计划

| 版本 | 清理任务 |
|------|----------|
| v0.2.0 | 添加类型注解、补充单元测试 |
| v0.3.0 | 性能基准测试、文档完善 |
| v0.4.0 | 代码重构、优化瓶颈 |
| v1.0.0 | 全面技术债务清理 |

---

## 风险管理

### 高风险项

**1. Verilog解析器复杂度**
- **影响**: 可能延期v0.5.0
- **概率**: 中
- **应对**:
  - 采用渐进式实现
  - 使用PyVerilog库
  - 社区反馈驱动

**2. 覆盖率数据库性能**
- **影响**: 大规模验证场景
- **概率**: 中
- **应对**:
  - 增量更新机制
  - 数据库持久化
  - 分页加载

### 中风险项

**1. 寄存器模型并发访问**
- **影响**: 多线程测试环境
- **概率**: 低
- **应对**:
  - 访问锁机制
  - 清晰的访问语义文档

**2. 开发资源限制**
- **影响**: 版本延期
- **概率**: 中
- **应对**:
  - 分阶段发布
  - 社区贡献
  - MVP优先

---

## 质量标准

每个版本发布前需要满足：

1. **功能完整性**: 所有计划功能实现
2. **测试覆盖率**: >80%单元测试覆盖
3. **文档完整性**: 所有公开API有文档
4. **性能基准**: 通过性能测试
5. **稳定性**: 0个critical bug

---

## 发布周期

### 发布节奏

- **小版本** (v0.x.1): bug修复、小功能
- **中版本** (v0.x.0): 新功能模块
- **大版本** (v1.0.0): 主要功能里程碑

### 发布流程

1. 功能开发完成
2. 代码审查
3. 测试验证
4. 文档更新
5. 发布候选版本
6. 社区反馈
7. 正式发布

---

## 社区参与

### 如何贡献

1. Fork项目
2. 创建功能分支
3. 提交Pull Request
4. 代码审查
5. 合并

### 贡献方向

- **bug修复**: 报告和修复bug
- **新功能**: 提出新功能建议并实现
- **文档**: 改进文档
- **测试**: 添加测试用例
- **示例**: 提供使用示例

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 联系方式

- **项目主页**: https://github.com/EdaerCoser/EDA_UFMV
- **问题反馈**: https://github.com/EdaerCoser/EDA_UFMV/issues
- **讨论区**: https://github.com/EdaerCoser/EDA_UFMV/discussions

---

## 附录

### A. 版本命名规范

- **v0.1.0**: 主版本.次版本.修订版本
- **主版本**: 重大架构变更（1.0.0开始）
- **次版本**: 新功能模块（0.2.0, 0.3.0...）
- **修订版本**: bug修复、文档更新（0.1.1, 0.1.2...）

### B. 时间估算说明

- **乐观估算**: 熟悉代码库，无重大障碍
- **现实估算**: 考虑学习曲线、调试时间
- **保守估算**: 包含缓冲时间，应对意外情况

### C. 里程碑验收标准

每个Milestone验收需满足：
1. 核心功能实现
2. 单元测试通过
3. 示例代码可用
4. 文档编写完成

---

**路线图最后更新**: 2026年3月1日
**下次审查**: v0.2.0开发启动时
**维护者**: EDA_UFMV开发团队
