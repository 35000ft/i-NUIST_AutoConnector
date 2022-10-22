# -*- coding:utf-8 -*-
import os
import shutil
import sys
import socket
import demjson3
import tkinter
import tkinter as tk
import getpass
from tkinter import ttk
# 调用Tk()创建主窗口
from tkinter import messagebox
import requests

__ISP_dict = {
    "中国移动": 2,
    "中国电信": 3,
    "中国联通": 4
}

url = 'http://a.nuist.edu.cn/api/v1/login'

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json;charset=UTF-8",
    "Host": "10.255.255.34",
    "Origin": "http://10.255.255.34",
    "Referer": "http://10.255.255.34/authentication/login",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
}


def get_ip():
    """
    获取在局域网的IP
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def set_data(channel, ifautologin, pagesign, password, username, usripadd):
    data = {
        "channel": channel,
        "ifautologin": ifautologin,
        "pagesign": pagesign,
        "password": password,
        "username": username,
        "usripadd": usripadd
    }
    return data


def parse_login_msg(login_info):
    print(login_info)
    if login_info['code'] == 200:
        return '登录成功'
    else:
        return '登录失败'


def login(username, password, ISP):
    _data = set_data(ISP, "1", "secondauth", password, username, get_ip())
    print(_data)
    response = requests.post(url=url, data=demjson3.encode(_data), headers=headers)
    response.encoding = 'utf-8'
    content = response.text
    obj = demjson3.decode(content, encoding='utf-8')
    return parse_login_msg(obj)


window = tk.Tk()
# 给主窗口起一个名字，也就是窗口的名字
window.title('i-NUIST Auto Connect')
# 设置窗口大小变量
width = 300
height = 180
# 窗口居中，获取屏幕尺寸以计算布局参数，使窗口居屏幕中央
screenwidth = window.winfo_screenwidth()
screenheight = window.winfo_screenheight()
size_geo = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
window.geometry(size_geo)


# 开启主循环，让窗口处于显示状态


def sub_login():
    username = e1.get()
    password = e2.get()
    ISP = parse_ISP(cbox.get())
    if ISP is None or ISP == "":
        messagebox.showerror('Error 400', '运营商不存在')
        return
    msg = ""
    for i in range(0, 3):
        msg = login(username, password, str(ISP))
        if msg == '登录成功':
            break
    remember_account(username, password, cbox.get(), is_auto_start.get())
    auto_start(is_auto_start.get())
    messagebox.showinfo('登录信息', msg)
    if msg == '登录成功':
        window.quit()


def remember_account(_username, _password, _ISP, _auto_start):
    with open('./data/account.dat', 'w', encoding='utf-8') as account_file:
        account_file.write(_username + '\n')
        account_file.write(_password + '\n')
        account_file.write(_ISP + '\n')
        account_file.write(str(_auto_start) + '\n')


def auto_complete():
    try:
        with open('./data/account.dat', 'r', encoding='utf-8') as account_file:
            info = account_file.readlines()
            e1.insert(0, info[0].strip())
            e2.insert(0, info[1].strip())
            cbox.set(info[2].strip())

            # 自动登录
            if len(info) == 4:
                _auto_start = int(info[3].strip())
                if _auto_start == 1:
                    sub_login()
    except FileNotFoundError as e:
        return


def auto_start(is_start):
    """
    开机启动
    :param is_start: 是否开机启动 1为开机启动
    :return:
    """
    is_start = int(is_start)
    program_name = os.path.basename(sys.argv[0])  # 获取自身文件名
    os_username = getpass.getuser()  # 获取用户名
    base_path = r'C:\\Users'
    base_path += '\\' + os_username + '\\' + r'AppData\\Roaming\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    start_dir = base_path  # 启动目录
    if is_start == 0:
        if os.path.exists(start_dir + '\\' + program_name):
            os.remove(start_dir + '\\' + program_name)
    elif is_start == 1:
        if os.path.exists(start_dir + '\\' + program_name):
            pass
        else:
            shutil.copy(program_name, start_dir)  # 复制文件到启动目录


def parse_ISP(_ISP):
    return __ISP_dict.get(_ISP)


# 运营商
def set_ISP(event):
    ISP_text.insert('insert', cbox.get() + "\n")


# 将俩个标签分别布置在第一行、第二行
tk.Label(window, text="账号:").grid(row=0, column=0)
tk.Label(window, text="密码:").grid(row=1, column=0)
tk.Label(window, text="运营商:").grid(row=2, column=0)

# 创建输入框控件
e1 = tk.Entry(window)
# 以 * 的形式显示密码
e2 = tk.Entry(window, show='*')

cbox = ttk.Combobox(window)
cbox['value'] = ('中国移动', '中国电信', '中国联通')
cbox.current(0)
cbox.bind("<<ComboboxSelected>>", set_ISP)
ISP_text = tkinter.Text(window)
is_auto_start = tk.IntVar()
check_is_auto_start = tk.Checkbutton(window, text="开机启动",
                                     variable=is_auto_start, onvalue=1, offvalue=0)

e1.grid(row=0, column=1, padx=5, pady=5)
e2.grid(row=1, column=1, padx=5, pady=5)
cbox.grid(row=2, column=1, padx=5, pady=5)
check_is_auto_start.grid(row=3, column=1, padx=15, pady=5)

# 使用 grid()的函数来布局，并控制按钮的显示位置
tk.Button(window, text="登录", width=10, command=sub_login).grid(row=4, column=0, sticky="w", padx=15, pady=5)
tk.Button(window, text="退出", width=10, command=window.quit).grid(row=4, column=1, sticky="e", padx=15, pady=5)
auto_complete()

window.mainloop()
