import subprocess

class HashUtility:
    
    @staticmethod
    def calculate_hash(data):
        openssl_cmd = ['openssl', 'dgst', '-sha3-256', '-hex']
        process = subprocess.Popen(openssl_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate(input=data.encode('utf-8'))
        hash_str = stdout.decode('utf-8')
        return hash_str.split('= ')[1].strip()