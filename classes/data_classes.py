class ReturnData:
    """
    Data class for returning data from functions

    :type response: bool
    :type message: str
    :type video: VideoClass child

    :param response: True if successful, False if not
    :param message: Message to be returned
    :param video: VideoClass child object to be returned if needed
    """
    def __init__(self, response: bool, message: str, video=None, terminate=False):
        self.response = response
        self.message = message
        self.video = video
        self.terminate = terminate
