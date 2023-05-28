# This file contains the Openssl bash commands as strings that will be used in the program.
# The commands are stored in a dictionary with the key being the name of the command and the value being the command itself.
# The commands are stored as strings so that they can be easily executed using the subprocess module.

commands = {
    # ECDSA keys
    "ECDSA_params_gen": lambda name, out_file: f'openssl ecparam -name {name} -out {out_file}',
    "ECDSA_params_view": lambda in_file: f'openssl ecparam -in {in_file} -text',
    "ECDSA_priv_key_gen": lambda param_file, out_file: f'openssl genpkey -paramfile {param_file} -out {out_file}',
    "ECDSA_priv_key_view": lambda in_file: f'openssl pkey -in {in_file} -text',
    "ECDSA_pub_key_gen": lambda priv_key_file, out_file: f'openssl pkey -in {priv_key_file} -pubout -out {out_file}',
    "ECDSA_pub_key_view": lambda in_file: f'openssl pkey -pubin -in {in_file} -text',
    # Certificate Signing Requests
    "CSR_gen": lambda priv_key_file, out_file, config_file: f'openssl req -new -key {priv_key_file} -out {out_file} -config {config_file}',
    "CSR_interactive_gen": lambda priv_key_file, out_file, config_file, f1, f2, f3, f4, f5, f6: f'openssl req -new -key {priv_key_file} -out {out_file} -config {config_file} -subj "/CN={f1}/C={f2}/ST={f3}/L={f4}/O={f5}/OU={f6}"',
    "CSR_view": lambda in_file: f'openssl req -in {in_file} -text',
    "cert_auto_sign": lambda days, priv_key_file, out_file, config_file: f'openssl req -new -x509 -days {days} -key {priv_key_file} -out {out_file} -config {config_file}',
    "auto_cert_view": lambda in_file: f'openssl x509 -in {in_file} -text',
    # CA creation
    "create_CA_main_dir": lambda ca_name: f'mkdir {ca_name}',
    "create_CA_key_dir": lambda ca_name: f'mkdir {ca_name}/private',
    "create_CA_cert_dir": lambda ca_name: f'mkdir {ca_name}/certs',
    "create_CA_index_file": lambda ca_name: f'touch {ca_name}/index.txt',
    "create_CA_serial_file": lambda ca_name: f'echo 00 > {ca_name}/serial',
    "move_CA_cert": lambda ca_name, cert_file: f'mv {cert_file} {ca_name}',
    "move_CA_key": lambda ca_name, priv_key_file: f'mv {priv_key_file} {ca_name}/private',
 }