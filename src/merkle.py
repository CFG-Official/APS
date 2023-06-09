import utils.hash_util as HU

def merkle_tree(leaves):
    """
        Funzione che prende in input una lista di foglie e restituisce la radice del Merkle Tree.
        Se il livello ha un numero dispari di nodi, l'ultimo nodo viene duplicato.
    """
    if len(leaves) % 2 != 0:
        leaves.append(leaves[-1])
    
    parent_nodes = []
    
    for i in range(0, len(leaves), 2):
        parent_node = HU.compute_hash_from_data(leaves[i] + leaves[i+1])
        parent_nodes.append(parent_node)
        
    if len(parent_nodes) == 1:
        return parent_nodes[0]
    else:
        return merkle_tree(parent_nodes)

def merkle_proof(leaves, index):
    """
        Funzione che prende in input una lista di foglie e un indice e restituisce la prova di Merkle per la foglia con indice index.
        La funzione richiede che la lista di foglie sia stata estesa con foglie duplicate se il numero non è una potenza di 2.
    """
    # Se sono alla radice non devo calcolare nessun livello superiore, restituisco
    if len(leaves) == 1:
        return [] # Nessuna come proof del livello

    # Non sono alla radice, calcolo il livello superiore
    parent_nodes = []

    # Calcolo i nodi genitori del livello successivo.
    for i in range(0, len(leaves), 2):
        parent_node = HU.compute_hash_from_data(leaves[i] + leaves[i + 1])
        parent_nodes.append(parent_node)

    proof = []
    proof.append(leaves[__sibling_index(index)])

    return proof + merkle_proof(parent_nodes, __parent_index(index))

def __sibling_index(index):
    if index % 2 == 0:
        return index + 1
    else:
        return index - 1

def __parent_index(index):
    return index // 2

def __preprocess(leaves):
    """
        Prende in input una lista di foglie, estende la lista con foglie duplicate se il numero non è una potenza di 2.
        Restituisce l'hash delle foglie.
    """

    extender = '$'

    while not __is_power_of_two(len(leaves)):
        leaves.append(extender)
    
    return [HU.compute_hash_from_data(leaf) for leaf in leaves]


def __is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

# Uso dell'algoritmo
# Leaves sono le foglie dell'albero, ovvero i dati da autenticare.
leaves = ['a', 'b', 'c']
leaves = __preprocess(leaves)
root = merkle_tree(leaves)
print(root)

print("PRIMO LIVELLO DELL'ALBERO")
print(leaves)

# Calcolo la prova di Merkle per la foglia con indice 2.
proof = merkle_proof(leaves, 0)
print("PROVA DI MERKLE")
print(proof)

