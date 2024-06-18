import logging
from concurrent.futures import ThreadPoolExecutor

class StockAgent:
    def __init__(self, products):
        self.stock = []  # Liste pour stocker les informations sur les stocks
        self.products = products  # Liste des produits associés aux travaux

    def update_stock(self, schedule):
        """
        Met à jour le stock en fonction du planning des machines.
        Utilise un ThreadPoolExecutor pour paralléliser les mises à jour des stocks.
        """
        with ThreadPoolExecutor() as executor:
            # Soumet les tâches de mise à jour du stock pour chaque tâche dans le planning
            futures = [executor.submit(self.update_task_stock, task) for machine_schedule in schedule for task in machine_schedule]
            for future in futures:
                # Ajoute le résultat de chaque future à la liste des stocks
                self.stock.append(future.result())

    def update_task_stock(self, task):
        """
        Met à jour le stock pour une tâche spécifique.
        Retourne un dictionnaire contenant l'ID du produit, la quantité (fixée à 1) et le temps de disponibilité.
        """
        job_id = task[0]  # ID du travail
        operation_id = task[1]  # ID de l'opération
        end_time = task[3]  # Temps de fin de l'opération
        for product in self.products:
            if product['job_id'] == job_id:
                # Journalise l'information de mise à jour du stock
                logging.info(f"Updating stock for job {job_id}, operation {operation_id}, end time {end_time}")
                # Retourne les informations mises à jour pour le stock
                return {'product_id': product['id'], 'quantity': 1, 'ready_time': end_time}

    def reduce_stock(self, product_id, quantity):
        """
        Réduit le stock pour un produit spécifique d'une certaine quantité.
        Retourne True si la réduction a réussi, sinon False.
        """
        for item in self.stock:
            if item['product_id'] == product_id and item['quantity'] >= quantity:
                item['quantity'] -= quantity
                # Journalise la réduction du stock
                logging.info(f"Reduced stock for product {product_id} by {quantity}")
                return True
        # Journalise un avertissement si le stock est insuffisant
        logging.warning(f"Insufficient stock for product {product_id}")
        return False

    def check_stock_availability(self, product_id, quantity):
        """
        Vérifie la disponibilité du stock pour un produit spécifique.
        Retourne True si la quantité demandée est disponible, sinon False.
        """
        total_quantity = sum(item['quantity'] for item in self.stock if item['product_id'] == product_id)
        return total_quantity >= quantity
    
    def aggregate_stock_by_jobs(self):
        """
        Agrège le stock par travail et retourne une liste triée d'éléments de stock agrégés.
        """
        aggregated_stock = {}
        for item in self.stock:
            product_id = item['product_id']
            ready_time = item['ready_time']
            if product_id in aggregated_stock:
                aggregated_stock[product_id] += ready_time
            else:
                aggregated_stock[product_id] = ready_time
        # Trie et formate l'agrégation des stocks
        sorted_aggregated_stock = [{'product_id': k, 'quantity': 1, 'ready_time': v} for k, v in sorted(aggregated_stock.items())]
        return sorted_aggregated_stock
