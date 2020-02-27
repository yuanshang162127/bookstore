from hashlib import sha1

def get_hash(str):
    sh = sha1()
    sh.update(str.encode('utf8'))
    result = sh.hexdigest()
    return result

