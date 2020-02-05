"""
localhost
---------
"""
import socket, os


def get_localhostname():
    if os.environ.get("DOC", False) == True:
        return socket.gethostname()
    else:
        return "sphinx-doc"


def get_ip_adress():
    if os.environ.get("DOC", False) == True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            pass
    return "123.4.567.890"


localhostname: str  #: the name of the local machine
localhostname = get_localhostname()

localhost: str  #: the localhost
localhost = "127.0.0.1"

localip: str  #: the local ip address
localip = get_ip_adress()
