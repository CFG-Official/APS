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
    
# RIFARE 
def merkle_proof(leaves, index):
    """
        Funzione che restituisce la prova di Merkle per un dato indice di foglia all'interno di un Merkle Tree.
    """
    if len(leaves) % 2 != 0:
        leaves.append(leaves[-1])

    parent_nodes = []

    for i in range(0, len(leaves), 2):
        parent_node = HU.compute_hash_from_data(leaves[i] + leaves[i + 1])
        parent_nodes.append(parent_node)

    if len(parent_nodes) == 1:
        if index == 0:
            return [], parent_nodes[0]
        else:
            return None  # L'indice specificato non corrisponde a una foglia presente nel Merkle Tree
    else:
        if index < len(parent_nodes):
            left_proof, left_hash = merkle_proof(parent_nodes[:index+1], index)
            right_proof, right_hash = merkle_proof(parent_nodes[index+1:], index)
            
            proof = [left_hash] + right_proof
            root_hash = HU.compute_hash_from_data(left_hash + right_hash)
            
            return proof, root_hash
        else:
            return None  # L'indice specificato non corrisponde a una foglia presente nel Merkle Tree


# Uso dell'algoritmo
# Leaves sono le foglie dell'albero, ovvero i dati da autenticare.
leaves = ['a', 'b', 'c', 'd', 'e']
leaves = [HU.compute_hash_from_data(leaf) for leaf in leaves] # Se le foglie sono pre-hashate non serve questa riga.
root = merkle_tree(leaves)
print(root)
