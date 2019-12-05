def get_localhostname():
    import socket

    return socket.gethostname()


localhostname: str  #: the localhosts name
localhostname = get_localhostname()
