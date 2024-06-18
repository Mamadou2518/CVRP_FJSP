import copy
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors



def read_cvrp_instance(file_path):
    """
    Lit une instance du CVRP depuis un fichier texte au format standard.
    
    Parameters:
        file_path (str): Le chemin vers le fichier d'instance.
        
    Returns:
        dict: Un dictionnaire contenant les coordonnées du dépôt, des clients, 
              les demandes des clients, et la capacité du véhicule.
              
              instance = 
              {
                'clients' : list(dict) => [{'id': 2, 'x': 626, 'y': 1111, 'demand': 1}, ...],
                'vehicle_capacity' : int => 25,
                'depot' = {'id': 1, 'x': 700, 'y': 1000, 'demand': 0},    
              }
    """
    instance = {}
    instance['clients'] = []
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
    reading_nodes = False
    reading_demands = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('CAPACITY'):
            instance['vehicle_capacity'] = int(line.split()[-1])
            
        elif line.startswith('NODE_COORD_SECTION'):
            reading_nodes = True
            reading_demands = False
            continue
        
        elif line.startswith('DEMAND_SECTION'):
            reading_nodes = False
            reading_demands = True
            continue
        
        elif line.startswith('DEPOT_SECTION'):
            reading_nodes = False
            reading_demands = False
            continue
        
        elif line == 'EOF':
            break
        
        if reading_nodes:
            parts = line.split()
            client_id = int(parts[0])
            x_coord = int(parts[1])
            y_coord = int(parts[2])
            if client_id == 1:
                instance['depot'] = {'id': client_id, 'x': x_coord, 'y': y_coord, 'demand': 0}
            else:
                instance['clients'].append({'id': client_id, 'x': x_coord, 'y': y_coord, 'demand': 0})
                
        elif reading_demands:
            parts = line.split()
            client_id = int(parts[0])
            demand = int(parts[1])
            if client_id != 1:
                for client in instance['clients']:
                    if client['id'] == client_id:
                        client['demand'] = demand
                        break
    
    return instance

def generate_initial_solution(instance):
    """
    Génère une solution initiale aléatoire pour le CVRP.
    
    Parameters:
        instance (dict): Un dictionnaire contenant les coordonnées du dépôt, des clients, 
                         les demandes des clients, et la capacité du véhicule.
        
    Returns:
        list: Une liste de routes, où chaque route est une liste de clients visités par un véhicule.
    """
    depot = instance['depot']
    clients = instance['clients']
    vehicle_capacity = instance['vehicle_capacity']
    
    random.shuffle(clients)
    
    routes = []
    current_route = []
    current_load = 0
    
    for client in clients:
        client_demand = client['demand']
        
        if current_load + client_demand <= vehicle_capacity:
            current_route.append(client)
            current_load += client_demand
        else:
            routes.append(current_route)
            current_route = [client]
            current_load = client_demand

    if current_route:
        routes.append(current_route)
    
    return routes

def generate_initial_solution_with_orders(instance, orders, stock_agent):
    """
    Génère une solution initiale pour le CVRP en tenant compte des commandes et du stock disponible.

    Args:
        instance (dict): L'instance CVRP contenant les informations des clients et du dépôt.
        orders (list): Liste des commandes, chaque commande contient 'client_id', 'product_id', et 'quantity'.
        stock_agent (StockAgent): L'agent responsable de la gestion du stock.

    Returns:
        list: Liste de routes pour chaque véhicule, où chaque route est une liste de clients visités.
    """
    # Récupère les informations sur le dépôt, les clients et la capacité des véhicules
    depot = instance['depot']
    clients = instance['clients']
    vehicle_capacity = instance['vehicle_capacity']

    # Mélange aléatoirement la liste des clients
    random.shuffle(clients)

    # Initialisation des routes et des variables de suivi
    routes = []
    current_route = []
    current_load = 0

    # Parcourt chaque commande dans la liste des commandes
    for order in orders:
        client_id = order['client_id']
        product_id = order['product_id']
        quantity = order['quantity']

        # Vérifie la disponibilité du stock pour la commande
        if stock_agent.check_stock_availability(product_id, quantity):
            # Trouve le client correspondant à la commande
            for client in clients:
                if client['id'] == client_id:
                    # Ajoute le client à la route actuelle si la capacité du véhicule le permet
                    if current_load + quantity <= vehicle_capacity:
                        current_route.append(client)
                        current_load += quantity
                        stock_agent.reduce_stock(product_id, quantity)
                    # Sinon, crée une nouvelle route et réinitialise la charge du véhicule
                    else:
                        routes.append(current_route)
                        current_route = [client]
                        current_load = quantity
                        stock_agent.reduce_stock(product_id, quantity)
                    break

    # Ajoute la dernière route à la liste des routes si elle n'est pas vide
    if current_route:
        routes.append(current_route)

    return routes


def calcul_distance(point1, point2):
    """
    Calcule la distance euclidienne entre deux points.

    Args:
        point1 (dict): Le premier point avec des coordonnées 'x' et 'y'.
        point2 (dict): Le deuxième point avec des coordonnées 'x' et 'y'.

    Returns:
        float: La distance euclidienne entre point1 et point2.
    """
    return np.sqrt((point1['x'] - point2['x'])**2 + (point1['y'] - point2['y'])**2)

def evaluate_route(route, instance):
    """
    Évalue la distance totale d'une route donnée pour un véhicule.

    Args:
        route (list): Liste des clients visités par le véhicule.
        instance (dict): L'instance CVRP contenant les informations des clients et du dépôt.

    Returns:
        float: La distance totale parcourue pour la route.
    """
    depot = instance['depot']
    total_distance = 0
    previous_client = depot

    # Ajoute les distances entre les clients successifs
    for client in route:
        total_distance += calcul_distance(previous_client, client)
        previous_client = client

    # Ajoute la distance pour revenir au dépôt
    total_distance += calcul_distance(previous_client, depot)

    return total_distance

def evaluate_solution(solution, instance):
    """
    Évalue la solution entière en calculant la distance totale parcourue par tous les véhicules.

    Args:
        solution (list): Liste de routes pour chaque véhicule.
        instance (dict): L'instance CVRP contenant les informations des clients et du dépôt.

    Returns:
        float: La distance totale parcourue pour la solution.
    """
    total_distance = 0

    # Calcule la distance totale pour chaque route et les additionne
    for route in solution:
        total_distance += evaluate_route(route, instance)

    return total_distance

def generate_neighbors(solution):
    """
    Génère des solutions voisines en échangeant des clients dans les routes.

    Args:
        solution (list): La solution actuelle.

    Returns:
        list: Liste des solutions voisines.
    """
    neighbors = []

    # Génère des voisins en échangeant des clients dans les routes
    for route_idx in range(len(solution)):
        route = solution[route_idx]
        for i in range(len(route)):
            for j in range(i + 1, len(route)):
                neighbor = copy.deepcopy(solution)
                neighbor[route_idx][i], neighbor[route_idx][j] = neighbor[route_idx][j], neighbor[route_idx][i]
                neighbors.append(neighbor)

    return neighbors

def tabu_search(instance, num_iterations, tabu_size):
    """
    Algorithme de recherche tabou pour optimiser les routes des véhicules.

    Args:
        instance (dict): L'instance CVRP contenant les informations des clients et du dépôt.
        num_iterations (int): Nombre d'itérations de l'algorithme.
        tabu_size (int): Taille de la liste tabou.

    Returns:
        list: La meilleure solution trouvée par l'algorithme.
    """
    # Génère une solution initiale
    current_solution = generate_initial_solution(instance)
    best_solution = current_solution
    best_cost = evaluate_solution(best_solution, instance)

    tabu_list = []

    for _ in range(num_iterations):
        # Génère des voisins de la solution actuelle
        neighbors = generate_neighbors(current_solution)
        best_neighbor = None
        best_neighbor_cost = float('inf')

        # Évalue chaque voisin et garde le meilleur
        for neighbor in neighbors:
            neighbor_cost = evaluate_solution(neighbor, instance)
            if neighbor_cost < best_neighbor_cost and neighbor not in tabu_list:
                best_neighbor = neighbor
                best_neighbor_cost = neighbor_cost

        if best_neighbor is not None:
            current_solution = best_neighbor
            if best_neighbor_cost < best_cost:
                best_solution = best_neighbor
                best_cost = best_neighbor_cost

            # Ajoute la solution actuelle à la liste tabou
            tabu_list.append(current_solution)
            if len(tabu_list) > tabu_size:
                tabu_list.pop(0)

    return best_solution

def plot_cvrp_routes(instance, solution, vehicle_departure_times):
    """
    Affiche les routes des véhicules pour une solution donnée.

    Args:
        instance (dict): L'instance CVRP contenant les informations des clients et du dépôt.
        solution (list): Liste de routes pour chaque véhicule.
        vehicle_departure_times (list): Liste des temps de départ des véhicules.
    """
    depot = instance['depot']

    plt.figure(figsize=(10, 8))

    colors = list(mcolors.TABLEAU_COLORS.keys())

    plt.scatter(depot['x'], depot['y'], c='red', marker='s', s=100, label=f'Depot')

    for idx, (route, depart_time) in enumerate(zip(solution, vehicle_departure_times)):
        route_color = colors[idx % len(colors)]

        route_coords = [(depot['x'], depot['y'])]

        for client in route:
            route_coords.append((client['x'], client['y']))
            plt.scatter(client['x'], client['y'], c=route_color)
            plt.annotate(f"{client['x']},{client['y']}", (client['x'], client['y']))

        route_coords.append((depot['x'], depot['y']))

        x_coords, y_coords = zip(*route_coords)

        plt.plot(x_coords, y_coords, color=route_color, label=f'Vehicle {idx + 1} (Departs: {depart_time})')

    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('CVRP Routes')
    plt.legend()
    plt.grid(True)
    plt.show()
