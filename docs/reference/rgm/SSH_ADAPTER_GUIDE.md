# SSH适配器使用指南

**版本**: v0.3.0
**最后更新**: 2026年3月1日

---

## 概述

SSHAdapter是EDA_UFVM RGM提供的硬件适配器，用于通过SSH协议远程访问FPGA单板的寄存器。它特别适用于：

- **远程FPGA板卡** - 通过网络访问实验室或数据中心板卡
- **嵌入式Linux系统** - 访问运行Linux的SoC板卡
- **多板卡测试** - 同时管理多个远程板卡
- **CI/CD集成** - 自动化测试远程硬件

---

## 快速开始

### 基本用法

```python
from rgm.adapters import SSHAdapter

# 创建SSH连接
ssh = SSHAdapter(
    host="192.168.1.100",
    username="fpga",
    password="boardpass"
)

# 连接并访问
ssh.connect()
value = ssh.read(0x40000000)
ssh.write(0x40000000, 0x12345678)
ssh.disconnect()
```

### 使用上下文管理器

```python
# 推荐：自动管理连接
with SSHAdapter(host="192.168.1.100", username="fpga", password="pass") as ssh:
    ssh.write(0x40000000, 0x1234)
    value = ssh.read(0x40000000)
```

### 与RGM集成

```python
from rgm import RegisterBlock, Register, Field, AccessType
from rgm.adapters import SSHAdapter
from rgm.access import FrontDoorAccess

# 创建寄存器模型
block = RegisterBlock("UART", base_address=0x40000000)
ctrl = Register("CTRL", 0x00, 32)
ctrl.add_field(Field("enable", 0, 1, AccessType.RW, 0))
block.add_register(ctrl)

# 设置SSH访问
ssh = SSHAdapter(host="192.168.1.100", username="fpga", password="pass")
frontdoor = FrontDoorAccess(ssh)
block.set_access_interface(frontdoor)

# 通过SSH访问远程单板
with ssh:
    block.write_field("CTRL", "enable", 1)
    enable = block.read_field("CTRL", "enable")
```

---

## 认证方式

### 密码认证

```python
ssh = SSHAdapter(
    host="192.168.1.100",
    username="fpga",
    password="your_password"
)
```

### 密钥认证

```python
ssh = SSHAdapter(
    host="192.168.1.100",
    username="fpga",
    key_filename="/path/to/private_key"
)
```

### SSH Agent（推荐）

```python
# 不提供密码或密钥，自动使用SSH agent
ssh = SSHAdapter(
    host="192.168.1.100",
    username="fpga"
)
```

---

## 自定义命令

SSHAdapter支持自定义读写命令模板，以适应不同的板卡软件环境。

### 默认命令模板

```python
# 默认模板
read_command="reg_read {address}"
write_command="reg_write {address} {value}"
```

### devmem命令（常见于嵌入式Linux）

```python
ssh = SSHAdapter(
    host="192.168.1.100",
    username="fpga",
    password="pass",
    read_command="devmem 0x{address}",
    write_command="devmem 0x{address} 32 0x{value}"
)
```

### 自定义脚本

```python
ssh = SSHAdapter(
    host="192.168.1.100",
    username="fpga",
    password="pass",
    read_command="/usr/local/bin/read_reg.py {address}",
    write_command="/usr/local/bin/write_reg.py {address} {value}"
)
```

### 命令占位符

| 占位符 | 说明 | 示例值 |
|:---|:---|:---|
| `{address}` | 寄存器地址 | `0x40000000` |
| `{value}` | 写入值 | `0x12345678` |

---

## 高级特性

### 获取统计信息

```python
ssh = SSHAdapter(host="192.168.1.100", username="fpga", password="pass")

with ssh:
    ssh.write(0x1000, 0x1111)
    ssh.write(0x2000, 0x2222)
    ssh.read(0x3000)

stats = ssh.get_statistics()
print(f"Host: {stats['host']}")
print(f"Connected: {stats['connected']}")
print(f"Read count: {stats['read_count']}")
print(f"Write count: {stats['write_count']}")
print(f"Total commands: {stats['total_commands']}")
```

### 执行自定义命令

```python
with SSHAdapter(host="192.168.1.100", username="fpga", password="pass") as ssh:
    # 执行自定义命令
    output = ssh.execute_custom_command("cat /proc/cpuinfo")
    print(output)

    # 读取板卡温度
    temp = ssh.execute_custom_command("cat /sys/class/thermal/thermal_zone0/temp")
    print(f"Temperature: {temp}")
```

### 错误处理

```python
from rgm.adapters import SSHAdapter

ssh = SSHAdapter(host="192.168.1.100", username="fpga", password="pass")

try:
    ssh.connect()
    value = ssh.read(0x40000000)
except RuntimeError as e:
    print(f"Connection failed: {e}")
finally:
    ssh.disconnect()
```

### 设置超时

```python
ssh = SSHAdapter(
    host="192.168.1.100",
    username="fpga",
    password="pass",
    timeout=30  # 30秒超时
)
```

---

## 多板卡管理

### 同时访问多个板卡

```python
from concurrent.futures import ThreadPoolExecutor

boards = [
    ("192.168.1.100", "board1"),
    ("192.168.1.101", "board2"),
    ("192.168.1.102", "board3"),
]

def read_board(host, name):
    with SSHAdapter(host=host, username="fpga", password="pass") as ssh:
        value = ssh.read(0x40000000)
        return name, value

# 并发读取多个板卡
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(lambda b: read_board(*b), boards)
    for name, value in results:
        print(f"{name}: 0x{value:08X}")
```

### 板卡配置管理

```python
class BoardConfig:
    def __init__(self, name, host, base_addr):
        self.name = name
        self.host = host
        self.base_addr = base_addr

boards = [
    BoardConfig("UART0", "192.168.1.100", 0x40000000),
    BoardConfig("UART1", "192.168.1.101", 0x40001000),
    BoardConfig("SPI", "192.168.1.102", 0x40002000),
]

for board in boards:
    with SSHAdapter(host=board.host, username="fpga", password="pass") as ssh:
        # 读取板卡ID寄存器
        board_id = ssh.read(board.base_addr + 0x00)
        print(f"{board.name} ID: 0x{board_id:08X}")
```

---

## CI/CD集成

### Jenkins Pipeline示例

```groovy
pipeline {
    agent any
    stages {
        stage('Test FPGA Boards') {
            steps {
                sh '''
                    python3 <<EOF
from rgm.adapters import SSHAdapter

boards = ["192.168.1.100", "192.168.1.101"]
for host in boards:
    with SSHAdapter(host=host, username="fpga", password="${FPGA_PASS}") as ssh:
        ssh.write(0x40000000, 0x12345678)
        value = ssh.read(0x40000000)
        assert value == 0x12345678, f"Test failed on {host}"
        print(f"Test passed on {host}")
EOF
                '''
            }
        }
    }
}
```

### GitHub Actions示例

```yaml
name: FPGA Tests

on: [push, pull_request]

jobs:
  test-boards:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install eda-ufmv
      - name: Test remote boards
        env:
          SSH_PASSWORD: ${{ secrets.SSH_PASSWORD }}
        run: |
          python <<EOF
from rgm.adapters import SSHAdapter
import os

hosts = ["192.168.1.100", "192.168.1.101"]
for host in hosts:
    with SSHAdapter(host=host, username="fpga", password=os.environ["SSH_PASSWORD"]) as ssh:
        ssh.write(0x40000000, 0x12345678)
        value = ssh.read(0x40000000)
        assert value == 0x12345678
        print(f"✓ {host} passed")
EOF
```

---

## 性能优化

### 连接复用

```python
# 推荐：复用连接
ssh = SSHAdapter(host="192.168.1.100", username="fpga", password="pass")
ssh.connect()

for i in range(100):
    ssh.write(0x40000000, i)
    value = ssh.read(0x40000000)

ssh.disconnect()

# 避免：每次都新建连接
for i in range(100):
    with SSHAdapter(...) as ssh:
        ssh.write(0x40000000, i)
```

### 批量操作

```python
# 使用update()批量写入
block.set(0x1111)
block.set(0x2222)
block.set(0x3333)
block.update()  # 一次网络操作
```

---

## 故障排查

### 连接失败

```python
# 检查网络连通性
import socket
try:
    socket.create_connection(("192.168.1.100", 22), timeout=5)
    print("Port 22 is reachable")
except socket.error:
    print("Cannot reach port 22")
```

### 权限问题

```python
# 确保SSH用户有权限访问/dev/mem或其他硬件接口
# 在板卡上执行：
# sudo chmod 666 /dev/mem
# 或将用户添加到相应组：
# sudo usermod -a -G kmem fpga
```

### 性能问题

```python
# 使用更快的命令
# 避免使用复杂的shell脚本
# 直接使用C程序或Python脚本
ssh = SSHAdapter(
    host="192.168.1.100",
    username="fpga",
    password="pass",
    read_command="/usr/local/bin/fast_read 0x{address}",
    write_command="/usr/local/bin/fast_write 0x{address} 0x{value}"
)
```

---

## 安全建议

1. **使用密钥认证** - 比密码更安全
2. **限制SSH用户权限** - 只授予必要的权限
3. **使用SSH配置文件** - 避免硬编码凭据
4. **定期更新密钥** - 提高安全性
5. **使用VPN** - 通过VPN访问远程板卡

```python
# 推荐：使用SSH配置文件
# ~/.ssh/config
# Host fpga-board
#     HostName 192.168.1.100
#     User fpga
#     IdentityFile ~/.ssh/fpga_key

ssh = SSHAdapter(
    host="fpga-board",  # 使用配置中的别名
    username=None,      # 从配置读取
    key_filename=None   # 从配置读取
)
```

---

## 完整示例

```python
from rgm import RegisterBlock, Register, Field, AccessType
from rgm.adapters import SSHAdapter
from rgm.access import FrontDoorAccess
import sys

def test_uart_on_remote_board():
    """测试远程板卡上的UART寄存器"""

    # 1. 创建寄存器模型
    block = RegisterBlock("UART", base_address=0x40000000)

    ctrl = Register("CTRL", 0x00, 32)
    ctrl.add_field(Field("enable", 0, 1, AccessType.RW, 0))
    ctrl.add_field(Field("mode", 1, 3, AccessType.RW, 0))
    block.add_register(ctrl)

    status = Register("STATUS", 0x04, 32)
    status.add_field(Field("tx_empty", 0, 1, AccessType.RO, 1))
    status.add_field(Field("rx_full", 1, 1, AccessType.RO, 0))
    block.add_register(status)

    # 2. 设置SSH访问
    ssh = SSHAdapter(
        host=sys.argv[1] if len(sys.argv) > 1 else "192.168.1.100",
        username="fpga",
        key_filename="~/.ssh/fpga_key",
        read_command="devmem 0x{address}",
        write_command="devmem 0x{address} 32 0x{value}"
    )

    frontdoor = FrontDoorAccess(ssh)
    block.set_access_interface(frontdoor)

    try:
        # 3. 连接并测试
        with ssh:
            print("Testing UART on remote board...")

            # 测试写入
            block.write_field("CTRL", "enable", 1)
            block.write_field("CTRL", "mode", 2)

            # 测试读取
            enable = block.read_field("CTRL", "enable")
            mode = block.read_field("CTRL", "mode")
            tx_empty = block.read_field("STATUS", "tx_empty")

            print(f"Enable: {enable}")
            print(f"Mode: {mode}")
            print(f"TX Empty: {tx_empty}")

            # 验证
            assert enable == 1, "Enable bit mismatch"
            assert mode == 2, "Mode mismatch"
            assert tx_empty == 1, "TX empty flag mismatch"

            print("All tests passed!")

            # 打印统计
            stats = ssh.get_statistics()
            print(f"Total commands: {stats['total_commands']}")

    except Exception as e:
        print(f"Test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    success = test_uart_on_remote_board()
    sys.exit(0 if success else 1)
```

---

## 相关文档

- [RGM_GUIDE.md](RGM_GUIDE.md) - RGM用户指南
- [ROADMAP.md](../development/ROADMAP.md) - 开发路线图

---

**文档维护**: EDA_UFVM开发团队
**最后更新**: 2026年3月1日
