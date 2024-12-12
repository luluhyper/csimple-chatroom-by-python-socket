import socket
import threading
from tkinter import *

host = '127.0.0.1'  # 设置服务器IP地址
port = 12345        # 设置服务器端口号
datesize = 1024     # 设置接收数据的最大字节数为 1024

# 聊天客户端类
class ClientChat:

    def __init__(self, master): # 初始化客户端
        self.master = master
        self.master.title("网络聊天室") # 设置窗口标题
        self.master.geometry("600x400") # 设置窗口大小


        self.clentname = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 创建客户端套接字对象

        #登陆界面
        self.login_frame = Frame(master)
        self.login_frame.pack(pady=150)
        # 用户名标签和输入框和登录按钮
        self.clientname_label = Label(self.login_frame, text="用户名:", font=("Arial", 12))
        self.clientname_label.grid(row=0, column=0, padx=5)
        self.clientname_input = Entry(self.login_frame, font=("Arial", 12))  # 用户名输入框
        self.clientname_input.grid(row=0, column=1, padx=5)
        self.name_button = Button(self.login_frame, text="登录", font=("Arial", 12), command=self.login)
        self.name_button.grid(row=0, column=2, padx=5)


        # 聊天界面
        self.chat_frame = Frame(master)
        self.chat_frame.pack_forget() # 隐藏聊天界面
        # 设置欢迎语
        self.welcome_label = Label(self.chat_frame, text="", font=("Arial", 14, "bold"), fg="green")
        self.welcome_label.grid(row=0, column=0, columnspan=2, pady=5)
        #聊天框（聊天窗口:显示聊天内容)
        self.chatroom = Text(self.chat_frame, state='disabled', wrap=WORD, font=("Arial", 14))
        self.chatroom.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        #设置聊天框内标签样式
        self.chatroom.tag_configure("提示信息", foreground="red", font=("Arial", 12, "bold"))
        self.chatroom.tag_configure("用户名", foreground="blue", font=("Arial", 14, "bold"))
        # 聊天框插入私聊提示
        self.chatroom.config(state='normal') # 设置文本框可编辑
        self.chatroom.insert(END,"私聊信息格式为 @用户名: 信息\n","提示信息")
        self.chatroom.config(state='disabled') # 设置文本框不可编辑

        # 在线用户列表界面(包含在聊天界面内）
        self.clientlist_frame = Frame(self.chat_frame)
        self.clientlist_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ns")
        # 在线用户标签和在线用户列表框
        self.clientlist_label = Label(self.clientlist_frame, text="在线用户", font=("Arial", 14, "bold"))
        self.clientlist_label.pack(pady=5)
        self.clientlist_text = Listbox(self.clientlist_frame, font=("Arial", 10), width=20)
        self.clientlist_text.pack(fill=BOTH, expand=True)

        # 聊天输入框
        self.chat_input = Entry(self.chat_frame, font=("Arial", 12))
        self.chat_input.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.send_button = Button(self.chat_frame, text="发送", font=("Arial", 12), command=self.send_message)
        self.send_button.grid(row=2, column=1, padx=5, pady=5)

        # 设置聊天窗口的布局
        self.chat_frame.rowconfigure(1, weight=1)
        self.chat_frame.columnconfigure(0, weight=1)

    def login(self): # 登录
        self.clentname = self.clientname_input.get().strip() # 获取用户名并去除两端的空白字符
        if not self.clentname:
            return
        try:
            self.client_socket.connect((host, port))
            self.client_socket.send(self.clentname.encode('utf-8'))  # 发送用户名
            self.login_frame.pack_forget()  # 隐藏登录界面
            self.chat_frame.pack(padx=10, pady=10, fill=BOTH, expand=True)  # 显示聊天界面
            self.welcome_label.config(text=f"你好，{self.clentname}！")  # 设置欢迎语
            threading.Thread(target=self.receive_message, daemon=True).start()  # 启动接收消息线程
        except Exception as e:
            print(f"无法连接服务器: {e}")

    def send_message(self):# 向服务端发送消息
        message = self.chat_input.get().strip() # 获取输入框中的消息并去除两端的空白字符
        if message:
           showmessage = f"{self.clentname}: {message}"
           self.update_chatroom(showmessage)
           self.client_socket.send(message.encode('utf-8')) #发送信息
           self.chat_input.delete(0, END) # 清空输入框

    def receive_message(self):# 接收来自服务端的消息
        while True:  # 循环接收消息
            try:
                message = self.client_socket.recv(datesize).decode('utf-8')
                if message.startswith("在线用户列表"):
                   clients = message[len("在线用户列表"):].split(",")
                   self.update_clientlist(clients)
                else:
                   self.update_chatroom(message)
            except Exception as e:
                print(f"消息接收错误: {e}")
                break

    def update_chatroom(self, message): # 更新聊天窗口的信息
        try:
            clientname, content = message.split(": ", 1)
        except ValueError:  # 防止消息格式不正确
            self.chatroom.config(state='normal')
            self.chatroom.insert(END, message + "\n")
            self.chatroom.config(state='disabled')
            return

        self.chatroom.config(state='normal')
        self.chatroom.insert(END, clientname + ": ", "用户名")    # 显示用户名
        self.chatroom.insert(END, content + "\n") # 显示消息内容
        self.chatroom.config(state='disabled')
        self.chatroom.see(END)

    def update_clientlist(self, clients): # 更新在线用户列表窗口的信息
        self.clientlist_text.delete(0, END)
        for client in clients:
            self.clientlist_text.insert(END, client)


if __name__ == '__main__':
    root = Tk()  # 创建Tkinter窗口对象
    client = ClientChat(root)  # 创建聊天客户端对象
    root.mainloop()  # 进入消息循环