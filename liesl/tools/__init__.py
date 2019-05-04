def get_localhostname():
    import socket
    return socket.gethostname()

localhostname = get_localhostname()