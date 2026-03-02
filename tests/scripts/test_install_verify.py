"""
EDA_UFVM 包安装验证脚本

验证所有模块是否可以正确导入
"""

print("=" * 60)
print("EDA_UFVM 包安装验证")
print("=" * 60)

print("\n[1] 导入 Randomization 模块...")
try:
    from sv_randomizer import Randomizable, rand, randc
    from sv_randomizer.api import constraint
    print("[OK] sv_randomizer 导入成功")
except Exception as e:
    print(f"[FAIL] sv_randomizer 导入失败: {e}")

print("\n[2] 导入 Coverage 模块...")
try:
    from coverage.core import CoverGroup, CoverPoint
    from coverage.core.bin import ValueBin, RangeBin
    print("[OK] coverage 导入成功")
except Exception as e:
    print(f"[FAIL] coverage 导入失败: {e}")

print("\n[3] 导入 RGM 模块...")
try:
    from rgm import RegisterBlock, Register, Field, AccessType
    print("[OK] rgm 导入成功")
except Exception as e:
    print(f"[FAIL] rgm 导入失败: {e}")

print("\n[4] 导入 SV to Python 模块...")
try:
    from sv_to_python import SVParser, UVMOperationExtractor, PythonGenerator
    print("[OK] sv_to_python 导入成功")
except Exception as e:
    print(f"[FAIL] sv_to_python 导入失败: {e}")

print("\n[5] 测试 SV to Python CLI...")
try:
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "sv_to_python", "--help"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("[OK] sv_to_python CLI 工作正常")
    else:
        print(f"[FAIL] sv_to_python CLI 错误: {result.stderr}")
except Exception as e:
    print(f"[FAIL] sv_to_python CLI 测试失败: {e}")

print("\n" + "=" * 60)
print("安装验证完成！")
print("=" * 60)

print("\n当前 Python 环境:")
import sys
print(f"  Python 版本: {sys.version}")
print(f"  Python 路径: {sys.executable}")

print("\n已安装的包:")
import pkg_resources
installed = []
for dist in pkg_resources.working_set:
    installed.append(f"  - {dist.project_name} {dist.version}")
print("\n".join(installed))

print("\n快速使用示例:")
print("\n  1. 随机化:")
print("     from sv_randomizer import Randomizable")
print("     from sv_randomizer.api import rand")
print("     class MyObj(Randomizable):")
print("         value: rand(int)(bits=16)")
print("     obj = MyObj()")
print("     obj.randomize()")

print("\n  2. 寄存器模型:")
print("     from rgm import RegisterBlock, Register, Field, AccessType")
print("     block = RegisterBlock('DMA', 0x40000000)")
print("     reg = Register('CTRL', 0x00, 32, 0x0)")
print("     reg.add_field(Field('ENABLE', 0, 1, AccessType.RW, 0))")
print("     block.add_register(reg)")

print("\n  3. SV转换:")
print("     python -m sv_to_python convert tasks.sv -o tasks.py")
