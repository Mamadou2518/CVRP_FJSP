import logging
from utils.cvrp_functions import tabu_search, generate_initial_solution_with_orders

class RoutingAgent:
    def __init__(self, instance, orders, stock_agent):
        """
        Initialisation de l'agent de routage avec les instances, commandes et agent de stock.
        
        Args:
            instance (dict): L'instance CVRP contenant les informations des clients et du dépôt.
            orders (list): Liste des commandes à traiter.
            stock_agent (StockAgent): Instance de l'agent de stock pour gérer les produits.
        """
        self.instance = instance  # L'instance CVRP
        self.orders = orders  # Les commandes à traiter
        self.stock_agent = stock_agent  # L'agent de stock pour gérer les produits

    def optimize_routes(self):
        """
        Optimise les routes des véhicules en utilisant une solution initiale et la recherche tabou.
        
        Returns:
            best_solution (list): La meilleure solution trouvée par l'algorithme de recherche tabou.
        """
        # Génère une solution initiale basée sur les commandes et l'état du stock
        initial_solution = generate_initial_solution_with_orders(self.instance, self.orders, self.stock_agent)
        
        # Applique l'algorithme de recherche tabou pour optimiser la solution initiale
        best_solution = tabu_search(self.instance, 100, 50)
        
        return best_solution  # Retourne la meilleure solution trouvée
