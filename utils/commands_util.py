# This file contains the Openssl bash commands as strings that will be used in the program.
# The commands are stored in a dictionary with the key being the name of the command and the value being the command itself.
# The commands are stored as strings so that they can be easily executed using the subprocess module.

openssl = "openssl" # insert the path to your openssl executable here

commands = {
    # Randomness extraction
    "rand_extract": lambda encode, num_bytes: f'{openssl} rand {encode} {num_bytes}',
    "rand_view": lambda in_file, decode: f'cat {in_file}',
    "rand_extract_bin": lambda out_file, num_bytes: f'{openssl} rand -out {out_file} {num_bytes}',
    "rand_extract_hex": lambda out_file, num_bytes: f'{openssl} rand -hex {num_bytes} >> {out_file}',
    "rand_extract_base64": lambda out_file, num_bytes: f'{openssl} rand -base64 {num_bytes} >> {out_file}',
    "rand_view_bin": lambda in_file: f'cat {in_file} | xxd -b',
    "rand_view_hex": lambda in_file: f'cat {in_file} | xxd -p',
    "rand_view_base64": lambda in_file: f'cat {in_file} | xxd -p | base64',
    # Hash
    "compute_hash_from_data": lambda data: f'printf {data} | openssl dgst -sha3-256 -hex',
    "compute_hash_from_file": lambda in_file, out_file, hash_alg: f'{openssl} dgst -{hash_alg} {in_file} >> {out_file}',
    # RSA keys
    "RSA_priv_key_gen": lambda out_file, num_bits: f'{openssl} genrsa -out {out_file} {num_bits}',
    "RSA_pub_key_export": lambda in_file, out_file: f'{openssl} rsa -pubout -in {in_file} -out {out_file}',
    "RSA_priv_key_view": lambda in_file: f'{openssl} rsa -in {in_file} -text',
    "RSA_pub_key_view": lambda in_file: f'{openssl} rsa -pubin -in {in_file} -text',
    "RSA_sign": lambda in_file, priv_key_file, signature: f'{openssl} pkeyutl -sign -in {in_file} -inkey {priv_key_file} -out {signature}',
    "RSA_verify": lambda in_file, signature, pub_key_file: f'{openssl} pkeyutl -verify -in {in_file} -sigfile {signature} -pubin -inkey {pub_key_file}',
    # ECDSA keys
    "ECDSA_params_gen": lambda name, out_file: f'{openssl} ecparam -name {name} -out {out_file}',
    "ECDSA_params_view": lambda in_file: f'{openssl} ecparam -in {in_file} -text',
    "ECDSA_priv_key_gen": lambda param_file, out_file: f'{openssl} genpkey -paramfile {param_file} -out {out_file}',
    "ECDSA_priv_key_view": lambda in_file: f'{openssl} pkey -in {in_file} -text',
    "ECDSA_pub_key_gen": lambda priv_key_file, out_file: f'{openssl} pkey -in {priv_key_file} -pubout -out {out_file}',
    "ECDSA_pub_key_view": lambda in_file: f'{openssl} pkey -pubin -in {in_file} -text',
    # Certificate Signing Requests
    "CSR_gen": lambda priv_key_file, out_file, config_file: f'{openssl} req -new -key {priv_key_file} -out {out_file} -config {config_file}',
    "CSR_interactive_gen": lambda priv_key_file, out_file, config_file, f1, f2, f3, f4, f5, f6: f'{openssl} req -new -key {priv_key_file} -out {out_file} -config {config_file} -subj "/CN={f1}/C={f2}/ST={f3}/L={f4}/O={f5}/OU={f6}"',
    "CSR_view": lambda in_file: f'{openssl} req -in {in_file} -text',
    "cert_auto_sign": lambda days, priv_key_file, out_file, config_file: f'{openssl} req -new -x509 -days {days} -key {priv_key_file} -out {out_file} -config {config_file}',
    "auto_cert_view": lambda in_file: f'{openssl} x509 -in {in_file} -text',
    # CA creation
    "create_CA_main_dir": lambda ca_name: f'mkdir {ca_name}',
    "create_CA_key_dir": lambda ca_name: f'mkdir {ca_name}/private',
    "create_CA_cert_dir": lambda ca_name: f'mkdir {ca_name}/certs',
    "create_CA_index_file": lambda ca_name: f'touch {ca_name}/index.txt',
    "create_CA_serial_file": lambda ca_name: f'echo 00 > {ca_name}/serial',
    "move_CA_cert": lambda ca_name, cert_file: f'mv {cert_file} {ca_name}',
    "move_CA_key": lambda ca_name, priv_key_file: f'mv {priv_key_file} {ca_name}/private',
    # CA sign CSR
    "sign_certificate": lambda in_file,out_file,config_file: f'{openssl} ca -in {in_file} -out {out_file} -policy policy_anything -config {config_file}',
    "sign_certificate_with_extensions": lambda in_file,out_file,config_file,extensions_file: f'{openssl} ca -in {in_file} -out {out_file} -policy policy_anything -config {config_file} -extfile {extensions_file}',
}
