import subprocess

def calculate_hash(data):
    openssl_cmd = ['openssl', 'dgst', '-sha256', '-hex']
    print(data,"\n")
    process = subprocess.Popen(openssl_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate(input=data.encode('utf-8'))
    hash_str = stdout.decode('utf-8')
    return hash_str.split('= ')[1].strip()

def merkle_tree(leaves):
    if len(leaves) % 2 != 0:
        leaves.append(leaves[-1])
    
    parent_nodes = []
    
    for i in range(0, len(leaves), 2):
        parent_node = calculate_hash(leaves[i] + leaves[i+1])
        parent_nodes.append(parent_node)
        
    if len(parent_nodes) == 1:
        return parent_nodes[0]
    else:
        return merkle_tree(parent_nodes)

# Uso dell'algoritmo
leaves = ['a', 'b', 'c', 'd', 'e']
leaves = [calculate_hash(leaf) for leaf in leaves]
root = merkle_tree(leaves)
print(root)
