class message_response:
    def __init__(self, status : bool = False, msg : str = "", e_msg : str = ""):
        self.status = status
        self.msg = msg
        self.error = e_msg
        self.result = {}
    def as_dict(self):
        '''Returns this object as a dict which flask can serialize to josn'''
        return{
            "actionSucceeded" : self.status,
            "message" : self.msg,
            "errorMessage" : self.error,
            **self.result
        }
        