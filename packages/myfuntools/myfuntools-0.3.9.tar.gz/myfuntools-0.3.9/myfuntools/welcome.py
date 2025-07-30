import ctypes
from ctypes import wintypes
import sys

# 定义Windows API
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# 结构体定义
class STARTUPINFOA(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPSTR),
        ("lpDesktop", wintypes.LPSTR),
        ("lpTitle", wintypes.LPSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", wintypes.LPBYTE),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]

def create_background_python_process(script_path):
    """创建后台运行的Python进程"""
    # 构造命令行
    python_exe = sys.executable  # 使用当前Python解释器
    cmd_line = f'"{python_exe}" "{script_path}"'
    
    # 准备结构体
    startup_info = STARTUPINFOA()
    startup_info.cb = ctypes.sizeof(STARTUPINFOA)
    startup_info.dwFlags = 0x1  # STARTF_USESHOWWINDOW
    startup_info.wShowWindow = 0  # SW_HIDE - 隐藏窗口
    
    process_info = PROCESS_INFORMATION()
    
    # 创建进程标志
    CREATE_NO_WINDOW = 0x08000000
    DETACHED_PROCESS = 0x00000008
    flags = CREATE_NO_WINDOW | DETACHED_PROCESS
    
    # 创建进程
    success = kernel32.CreateProcessA(
        None,                       # 应用程序名(使用命令行)
        cmd_line.encode('utf-8'),   # 命令行
        None,                       # 进程安全属性
        None,                       # 线程安全属性
        False,                      # 不继承句柄
        flags,                      # 创建标志
        None,                       # 环境块
        None,                       # 当前目录
        ctypes.byref(startup_info),
        ctypes.byref(process_info)
    )
    
    if not success:
        error = ctypes.get_last_error()
        raise ctypes.WinError(error)
    
    print(f"后台进程已启动，PID: {process_info.dwProcessId}")
    
    # 关闭不再需要的句柄
    kernel32.CloseHandle(process_info.hProcess)
    kernel32.CloseHandle(process_info.hThread)
    
    return process_info.dwProcessId

# showtime.py脚本内容
SHOWTIME_SCRIPT = """
import time
from datetime import datetime

while True:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("time.txt", "a") as f:
        f.write(f"{current_time}\\n")
    time.sleep(1)
"""

if __name__ == "__main__":
    # 1. 创建showtime.py脚本文件
    with open("showtime.py", "w") as f:
        f.write(SHOWTIME_SCRIPT)
    
    # 2. 创建后台进程
    try:
        pid = create_background_python_process("showtime.py")
        print(f"时间记录脚本已在后台运行(PID: {pid})")
        print("输出将写入到time.txt，按任意键退出...")
        input()  # 等待用户按键退出
    except Exception as e:
        print(f"错误: {e}")
    finally:
        print("主程序退出")
