from hash import HashUtility

def merkle_tree(leaves):
    """
        Funzione che prende in input una lista di foglie e restituisce la radice del Merkle Tree.
        Se il livello ha un numero dispari di nodi, l'ultimo nodo viene duplicato.
    """
    if len(leaves) % 2 != 0:
        leaves.append(leaves[-1])
    
    parent_nodes = []
    
    for i in range(0, len(leaves), 2):
        parent_node = HashUtility.calculate_hash(leaves[i] + leaves[i+1])
        parent_nodes.append(parent_node)
        
    if len(parent_nodes) == 1:
        return parent_nodes[0]
    else:
        return merkle_tree(parent_nodes)

# Uso dell'algoritmo
# Leaves sono le foglie dell'albero, ovvero i dati da autenticare.
leaves = ['a', 'b', 'c', 'd', 'e']
leaves = [HashUtility.calculate_hash(leaf) for leaf in leaves] # Se le foglie sono pre-hashate non serve questa riga.
root = merkle_tree(leaves)
print(root)
