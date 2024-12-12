import socket
import threading

host = '0.0.0.0'  # 设置服务器监听的主机地址为 0.0.0.0，表示监听所有可用的网络接口
port = 12345      # 设置服务器监听的端口号为 12345
datesize = 1024   # 设置接收数据的最大字节数为 1024

# 创建在线用户字典：{用户名: (连接, 地址)}
clients ={}

# 遍历所有在线用户,进行广播信息
def broadcast(message,selfname=None):
  for clientname,(conn,_) in clients.items():
      if clientname != selfname: # 不发送给自己
          try:
              conn.send(message.encode('utf-8'))
          except:
              pass

# 广播在线用户列表
def broadcast_clients_list():
    client_list =",".join(clients.keys()) #将用户名用逗号连接成一个字符串
    for conn,_ in clients.values():
        try:
            conn.send(f"在线用户列表{client_list}".encode('utf-8')) #发送在线用户列表
        except:
            pass

# 处理单个客户端的连接请求
def handle_client(conn,adrr):
    try:
        clientname = conn.recv(datesize).decode('utf-8') #接受客户端发送的用户名
        if not clientname:
            conn.close()
            return

        clients[clientname]=(conn,adrr)  # 添加新客户端连接和地址到在线用户字典中，进行更新
        print(f"{clientname} 加入了聊天室 ；地址信息：{adrr}")  # 在服务端打印客户端加入信息，进行记录
        broadcast(f"{clientname} 加入了聊天室！", selfname=clientname) #广播新用户加入信息
        broadcast_clients_list() #更新广播在线用户列表

        while True: # 循环接收客户端发送的消息
            message = conn.recv(datesize).decode('utf-8')
            if message.startswith("@"): # 私聊消息，格式为 @目标用户名:消息
                try:
                    target_client,private_message=message[1:].split(":",1)
                    if target_client in clients:
                        target_coon=clients[target_client][0] # 获取目标用户的连接
                        target_coon.send(f"[私聊]{clientname}: {private_message}".encode('utf-8')) # 发送私聊消息
                    else:
                        conn.send("你私聊的用户不在线！".encode('utf-8'))
                except:
                    conn.send("你的私聊格式错误！应为 @目标用户名:消息".encode('utf-8'))

            else:
                broadcast(f"{clientname}:{message}", selfname=clientname) # 群聊消息

    except (ConnectionResetError, BrokenPipeError):
        pass

    finally:
        conn.close() # 客户端关闭连接
        if clientname in clients:
            del clients[clientname]
            print(f"{clientname} 离开了聊天室")  #在服务端打印客户端离开信息，进行记录
            broadcast(f"{clientname} 离开了聊天室！", selfname=clientname)
            broadcast_clients_list()  #更新广播在线用户列表

# 启动服务器
def start_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #创建服务端套接字对象

    server_socket.bind((host,port)) #绑定主机和端口
    server_socket.listen(5)  # 监听连接请求
    print("服务端已经启动，等待客户端连接...")

    while True: # 循环接收客户端连接请求
        conn,adrr = server_socket.accept() # 接受客户端连接
        print(f"来自{adrr}的新连接")
        threading.Thread(target=handle_client, args=(conn, adrr), daemon=True).start() #创建新线程处理客户端连接请求

if __name__ == "__main__":
    start_server()
















