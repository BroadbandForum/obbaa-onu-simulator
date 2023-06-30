class ConnectionInfo:

    @staticmethod
    def set_connection(server):
        ConnectionInfo.server = server

    @staticmethod  
    def get_connection():
        return ConnectionInfo.server

    @staticmethod
    def set_addr(addr):
        ConnectionInfo.addr = addr

    @staticmethod  
    def get_addr():
        return ConnectionInfo.addr
    
