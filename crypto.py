import base64
class Crypto:
 key = "njwef34r38wefwuhuh3"
 def encrypt(self,msg):
    encryped = []
    for i, c in enumerate(msg):
        key_c = ord(self.key[i % len(self.key)])
        msg_c = ord(c)
        encryped.append(chr((msg_c + key_c) % 127))
    return ''.join(encryped)

 def decrypt(self,encryped):
    msg = []
    for i, c in enumerate(encryped):
        key_c = ord(self.key[i % len(self.key)])
        enc_c = ord(c)
        msg.append(chr((enc_c - key_c) % 127))
    return ''.join(msg)
 def b64enc(self,text):
     return (base64.b64encode(text.encode())).decode()
 def b64dec(self,text):
     return (base64.b64decode(text.encode())).decode()