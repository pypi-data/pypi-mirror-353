from cryptography.fernet import Fernet
import ctypes
from ctypes import wintypes
from ctypes import c_void_p

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# 常量定义
CREATE_BREAKAWAY_FROM_JOB = 0x01000000
CREATE_UNICODE_ENVIRONMENT = 0x00000400

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


def force_unload_dll(dll_name):
    """通过枚举进程模块强制卸载"""
    PROCESS_ALL_ACCESS = 0x1F0FFF
    h_snapshot = kernel32.CreateToolhelp32Snapshot(0x00000008, 0)  # TH32CS_SNAPMODULE
    if h_snapshot == -1:
        print("创建快照失败")
        return
    
    class MODULEENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("th32ModuleID", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("GlblcntUsage", wintypes.DWORD),
            ("ProccntUsage", wintypes.DWORD),
            ("modBaseAddr", wintypes.LPVOID),
            ("modBaseSize", wintypes.DWORD),
            ("hModule", wintypes.HMODULE),
            ("szModule", ctypes.c_char * 256),
            ("szExePath", ctypes.c_char * 260)
        ]
    
    entry = MODULEENTRY32()
    entry.dwSize = ctypes.sizeof(MODULEENTRY32)
    
    if kernel32.Module32First(h_snapshot, ctypes.byref(entry)):
        while True:
            if dll_name.lower() in entry.szModule.decode().lower():
                print(f"找到模块: {entry.szModule.decode()}")
                kernel32.FreeLibrary.argtypes = [c_void_p]
                if kernel32.FreeLibrary(entry.hModule):
                    print("卸载成功")
                else:
                    print("卸载失败")
            if not kernel32.Module32Next(h_snapshot, ctypes.byref(entry)):
                break
    
    kernel32.CloseHandle(h_snapshot)


def main():
    # 准备参数
    startup_info = STARTUPINFOA()
    startup_info.cb = ctypes.sizeof(startup_info)
    process_info = PROCESS_INFORMATION()

    exe_path = 'pythonw.exe'
    cmd_args = '''-c "import time; exec('while True:print(time.time());time.sleep(5)')"'''
    

    cmd_line = f'"{exe_path}"'
    if cmd_args:
        cmd_line += f" {cmd_args}"
    cmd_line_buffer = ctypes.create_string_buffer(cmd_line.encode('utf-8'))
    
    print(cmd_line)

    flags = CREATE_BREAKAWAY_FROM_JOB

    # 创建进程
    success = kernel32.CreateProcessA(
        None,                   # 应用程序名
        cmd_line_buffer,        # 命令行
        None,                   # 进程安全属性
        None,                   # 线程安全属性
        False,                  # 不继承句柄
        flags,                  # 创建标志
        None,                   # 环境块
        None,                   # 当前目录
        ctypes.byref(startup_info),
        ctypes.byref(process_info)
    )
    
    if success:
        print("进程创建成功")
        kernel32.CloseHandle(process_info.hProcess)
        kernel32.CloseHandle(process_info.hThread)


if __name__ == "__main__":
    h_module = kernel32.GetModuleHandleA("python313.dll".encode())
    print(f"模块句柄: {h_module}")
    force_unload_dll("python313.dll")


    h_module = kernel32.GetModuleHandleA("python.dll".encode())
    print(f"模块句柄: {h_module}")
    force_unload_dll("python.dll")
    main()
