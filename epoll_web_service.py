#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket
import sys
import re
import time
import select


class WSGI():
    def __init__(self, port):
        # 创建套接字
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置套接字，服务器端第四次挥手后立刻释放资源
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        # 绑定端口
        self.server_socket.bind(("", port))
        # 将套接字设置为监听状态
        self.server_socket.listen(128)
        self.DOCUMENT = "./html"
        # 创建epoll对象
        self.epoll = select.epoll()
        # 将创建的套接字添加到epoll的事件监听中
        self.epoll.register(self.server_socket.fileno(),select.EPOLLIN|select.EPOLLET)

    def nostop_server(self):
        """等待客户端到来"""
        epoll_dict = dict()
        
        while True:
            epoll_list = self.epoll.poll() 
            for fd,event in epoll_list:
                # 对事件进行判断,是否是新的客户端接入还是客户端发来数据
                if fd == self.server_socket.fileno():
                    self.client_socket, client_addr = self.server_socket.accept()
                    self.epoll.register(self.client_socket.fileno())
                    epoll_dict[self.client_socket.fileno()] = self.client_socket
                else:
                    data = epoll_dict[fd].recv(1024)
                    if data:
                        self.handle(data)
                    else:
                        self.client_socket.close()
                        self.epoll.unregister(fd)
                        del epoll_dict[fd]
        # 关闭为客服端服务的套接字
        self.server_socket.close()

    def handle(self,client_data):
        """处理收到的数据，根据数据发送内容 """
        client_data =client_data.decode("utf-8", errors="ignore")
        client_data = client_data.splitlines()
        # 获取数据的第一行内容中，客户端请求的内容
        file_name = re.match(r"[^/]+(/[^ ]*)", client_data[0]).group(1)
        if file_name:
            if file_name == "/":
                file_name = "/index.html"
            else:
                file_name = file_name
        try:
            f = open(self.DOCUMENT + file_name, "rb")
        except:
            # 如果客户端访问的内容不存在
            res_body = "未找到该页面"
            res_head = "HTTP/ 404 Forbidden\r\n"
            res_head += "Content-Type:text/html;charset=utf-8\r\n"   
            res_head += "Content-Length:%s\r\n" % (len(res_body.decode("utf-8")))
            res_head += "\r\n"
            msg = res_head + res_body
            self.client_socket.send(msg.encode("utf-8"))
        else:
            # 如果客户端想访问的内容存在，读取并发送
            content = f.read()
            res_body = content
            res_head = "HTTP/ 200 OK\r\n"
            res_head += "Content-Type:text/html;charset=utf-8\r\n"   
            res_head += "Content_Length:%s\r\n" % (len(res_body))
            res_head += "\r\n"
            self.client_socket.send(res_head.encode("utf-8"))
            self.client_socket.send(res_body)
        self.client_socket.close()

def main():
    """主控制程序"""
    # 指定一个端口
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        return
    wsgi = WSGI(port)
    wsgi.nostop_server()

if __name__ == "__main__":
    main()
