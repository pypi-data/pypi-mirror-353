from cryptography.fernet import Fernet
import ctypes
from ctypes import wintypes

# 定义必要的常量和函数
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)

# 常量定义
CREATE_NO_WINDOW = 0x08000000
CREATE_BREAKAWAY_FROM_JOB = 0x01000000
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100

ULONG_PTR = ctypes.c_ulonglong

# 结构体定义
class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("nLength", wintypes.DWORD),
        ("lpSecurityDescriptor", wintypes.LPVOID),
        ("bInheritHandle", wintypes.BOOL),
    ]

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

class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", wintypes.LARGE_INTEGER),
        ("PerJobUserTimeLimit", wintypes.LARGE_INTEGER),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ULONG_PTR),  # 使用自定义类型
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]

# 创建限制性进程
def main():
    """创建受限制的新进程"""
    # 准备参数
    startup_info = STARTUPINFOA()
    startup_info.cb = ctypes.sizeof(STARTUPINFOA)
    process_info = PROCESS_INFORMATION()

    exe_path = r'C:\Users\intC\AppData\Local\Programs\Python\Python313\pythonw.exe'
    cmd_args = '''-c "import time; exec('while True:print(time.time());time.sleep(5)')"'''

    # 构造命令行
    cmd_line = f'"{exe_path}"'
    if cmd_args:
        cmd_line += f" {cmd_args}"
    cmd_line_buffer = ctypes.create_string_buffer(cmd_line.encode('utf-8'))
    
    # 创建安全属性
    sa = SECURITY_ATTRIBUTES()
    sa.nLength = ctypes.sizeof(SECURITY_ATTRIBUTES)
    sa.lpSecurityDescriptor = None
    sa.bInheritHandle = False
    
    # 创建标志 - 禁止创建新窗口
    flags = CREATE_NO_WINDOW

    print(cmd_line_buffer,cmd_line)
    
    # 创建进程
    success = kernel32.CreateProcessA(
        None,                   # 应用程序名
        cmd_line_buffer,        # 命令行
        ctypes.byref(sa),      # 进程安全属性
        ctypes.byref(sa),      # 线程安全属性
        False,                  # 不继承句柄
        flags,                  # 创建标志
        None,                   # 环境块
        None,                   # 当前目录
        ctypes.byref(startup_info),
        ctypes.byref(process_info)
    )
    
    if not success:
        error = ctypes.get_last_error()
        raise ctypes.WinError(error)
    
    print(f"成功创建进程，PID: {process_info.dwProcessId}")
    
    # 创建作业对象限制进程行为
    h_job = kernel32.CreateJobObjectW(None, None)
    if not h_job:
        error = ctypes.get_last_error()
        print(f"创建作业对象失败: {error}")
        return process_info
    
    # 设置作业对象限制
    info = JOBOBJECT_BASIC_LIMIT_INFORMATION()
    info.LimitFlags = JOB_OBJECT_LIMIT_PROCESS_MEMORY
    
    # 将进程分配给作业对象
    if not kernel32.AssignProcessToJobObject(h_job, process_info.hProcess):
        error = ctypes.get_last_error()
        print(f"分配进程到作业对象失败: {error}")
    
    return process_info


if __name__ == "__main__":

    # h_module = kernel32.GetModuleHandleA("python313.dll".encode())
    # print(f"模块句柄: {h_module}")
    # force_unload_dll("python313.dll")


    # h_module = kernel32.GetModuleHandleA("python.dll".encode())
    # print(f"模块句柄: {h_module}")
    # force_unload_dll("python.dll")
    main()
