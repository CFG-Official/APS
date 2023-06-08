
from pyasn1.codec.der.decoder import decode
from pyasn1.codec.der.encoder import encode
import subprocess


class CertificateAuthority:

    def calculate_signature(asn1_file, private_key_file):
        # Carico il file ASN.1
        with open(asn1_file, 'rb') as f:
            asn1_data = f.read()

        # Estraggo la sequenza TBS Certificate (si trova all'offset 4 e ha lunghezza 370, secondo il tuo output di openssl asn1parse)
        tbs_certificate = decode(asn1_data)[0][0]

        # Salvo il TBS Certificate in un file temporaneo
        with open('tbs_certificate.der', 'wb') as f:
            f.write(encode(tbs_certificate))

        # Uso openssl per firmare il TBS Certificate con la chiave privata
        openssl_cmd = ['openssl', 'dgst', '-sha256', '-sign', private_key_file, '-out', 'signature.bin', 'tbs_certificate.der']
        subprocess.check_call(openssl_cmd)

        # Leggo e restituisco la firma
        with open('signature.bin', 'rb') as f:
            signature = f.read()

        return signature
