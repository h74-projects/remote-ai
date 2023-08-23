import datetime

class Encoder:
    def __init__(self, topic, source, roi_face):
        self.m_time = datetime.datetime.now()
        self.m_topic = topic
        self.m_source = source
        for (x, y, w, h) in roi_face:   
            self.m_face = f"{x}|{y}|{w}|{h}"
        
        self.m_message = ''

    def encode(self):
        self.m_message = f"{self.m_topic}|{self.m_time}|{self.m_source}|{self.m_face}"
        return str(self.m_message)
    
# if __name__ == "__main__":
#     encoder_instance = Encoder("face", "nisan", [(295,199,137,137)])
#     print(encoder_instance.encode())
