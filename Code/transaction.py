import time

class Transaction:
    """
    Represents a transaction between two parties, including robot's panorama and common landmarks.
    Arguments:
        id (int): A unique identifier for the transaction.
        #size (float): The size of the transaction.
        sender (str): The sender of the transaction.
        panorama (list of str): The panorama images collected by the sender.
        com_landmarks (list): A list of common landmarks of the sender with the other nodes.
        nonce (int): A unique number (increase based on sender) it prevents replay attacks or unordered messages.
    """


    def __init__(self, id: int, sender: str, panorama:list ,partner: str, com_landmarks: list, nonce: int):
        self.id = id
        #self.size = size
        self.sender = sender
        self.panorama = panorama
        self.partner = partner
        self.com_landmarks=com_landmarks
        self.nonce=nonce
        self.timestamp = time.ctime()
        #self.signature = signature


    def __repr__(self):
        return str(self.id)

    def details(self):
        """
        Print the transaction details.
        """
        print("\t\tTransaction id    : ", self.id)
        #print("\t\t\tTransaction Size : ", self.size)
        print("\t\t\tSender            : ", self.sender)
        print("\t\t\tPartner           : ", self.partner)
        #print("\t\t\tPanorama         : ", self.panorama)
        print("\t\t\tCommon Landmarks  : ", self.com_landmarks)
        print("\t\t\tNonce             : ", self.nonce)
        print("\t\t\tTime              : ", self.timestamp)
        
    def metric(self):
        """
        return the transaction details.
        """
        return  [self.id, self.sender, self.nonce, self.partner, self.com_landmarks, self.timestamp]
