"""
SSH Remote Board Adapter

Support accessing real FPGA boards via SSH for remote register access.
"""

import socket
from typing import Optional, Dict, Any
from .base import HardwareAdapter


class SSHAdapter(HardwareAdapter):
    """
    SSH远程板卡适配器

    通过SSH连接到远程FPGA板卡，执行寄存器读写命令。

    Args:
        host: SSH主机地址（如"192.168.1.100"或"board.example.com"）
        port: SSH端口（默认22）
        username: SSH用户名
        password: SSH密码（可选，也可使用密钥认证）
        key_filename: SSH私钥文件路径（可选）
        timeout: 连接超时时间（秒，默认10）
        read_command: 读取寄存器的命令模板
        write_command: 写入寄存器的命令模板

    Example:
        >>> adapter = SSHAdapter(
        ...     host="192.168.1.100",
        ...     username="fpga",
        ...     password="boardpass"
        ... )
        >>> adapter.connect()
        >>> value = adapter.read(0x4000_0000)

    Command Templates:
        read_command: 命令应包含{address}占位符
            默认: "reg_read {address}"
            示例: "devmem 0x{address}"

        write_command: 命令应包含{address}和{value}占位符
            默认: "reg_write {address} {value}"
            示例: "devmem 0x{address} 32 0x{value}"
    """

    def __init__(
        self,
        host: str,
        username: str,
        port: int = 22,
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        timeout: int = 10,
        read_command: str = "reg_read {address}",
        write_command: str = "reg_write {address} {value}",
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.timeout = timeout
        self.read_command = read_command
        self.write_command = write_command

        # SSH连接
        self._client = None
        self._connected = False

        # 命令执行统计
        self._read_count = 0
        self._write_count = 0

    def connect(self) -> bool:
        """
        连接到SSH服务器

        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to import paramiko
            import paramiko

            # 创建SSH客户端
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 连接参数
            connect_args = {
                "hostname": self.host,
                "port": self.port,
                "username": self.username,
                "timeout": self.timeout,
            }

            # 认证方式
            if self.key_filename:
                connect_args["key_filename"] = self.key_filename
            elif self.password:
                connect_args["password"] = self.password
            else:
                # 尝试使用默认SSH agent
                connect_args["look_for_keys"] = True
                connect_args["allow_agent"] = True

            # 建立连接
            self._client.connect(**connect_args)
            self._connected = True
            return True

        except ImportError:
            raise RuntimeError(
                "SSH adapter requires 'paramiko' library. "
                "Install it with: pip install paramiko"
            )
        except Exception as e:
            raise RuntimeError(f"SSH connection failed: {e}")

    def disconnect(self) -> None:
        """断开SSH连接"""
        if self._client:
            self._client.close()
            self._client = None
            self._connected = False

    def _execute_command(self, command: str) -> str:
        """
        执行SSH命令并返回输出

        Args:
            command: 要执行的命令

        Returns:
            命令输出（stdout）
        """
        if not self._connected or not self._client:
            raise RuntimeError("SSH not connected")

        stdin, stdout, stderr = self._client.exec_command(command)
        output = stdout.read().decode("utf-8").strip()
        error = stderr.read().decode("utf-8").strip()

        if error:
            raise RuntimeError(f"SSH command failed: {error}")

        return output

    def read(self, address: int) -> int:
        """
        通过SSH读取寄存器

        Args:
            address: 物理地址

        Returns:
            读取到的值
        """
        # 格式化读取命令
        command = self.read_command.format(address=hex(address))

        # 执行命令
        output = self._execute_command(command)

        # 解析返回值（假设返回十六进制值）
        try:
            # 移除可能的"0x"前缀
            if output.startswith("0x") or output.startswith("0X"):
                value = int(output, 16)
            else:
                value = int(output)
        except ValueError:
            raise RuntimeError(
                f"Cannot parse read result as integer: '{output}'"
            )

        self._read_count += 1
        return value

    def write(self, address: int, value: int) -> None:
        """
        通过SSH写入寄存器

        Args:
            address: 物理地址
            value: 要写入的值
        """
        # 格式化写入命令
        command = self.write_command.format(
            address=hex(address),
            value=hex(value)
        )

        # 执行命令
        self._execute_command(command)
        self._write_count += 1

    def is_connected(self) -> bool:
        """检查SSH连接状态"""
        return self._connected and self._client is not None

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取SSH访问统计信息

        Returns:
            包含统计信息的字典
        """
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "connected": self._connected,
            "read_count": self._read_count,
            "write_count": self._write_count,
            "total_commands": self._read_count + self._write_count,
        }

    def execute_custom_command(self, command: str) -> str:
        """
        执行自定义SSH命令（高级用法）

        Args:
            command: 要执行的命令

        Returns:
            命令输出
        """
        return self._execute_command(command)

    def __repr__(self) -> str:
        return (
            f"SSHAdapter(host={self.host}, port={self.port}, "
            f"user={self.username}, connected={self._connected})"
        )

    def __enter__(self):
        """支持上下文管理器（with语句）"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持上下文管理器（with语句）"""
        self.disconnect()
