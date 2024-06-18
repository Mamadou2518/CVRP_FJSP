import logging
import random
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor
from scheduling_agent import test_RS
from stock_agent import StockAgent
from cvrp_agent import RoutingAgent
from utils import commun_functions, cvrp_functions
from utils.diagram import diagram
import matplotlib.pyplot as plt
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

file_path = 'Instances/5_Kacem/Kacem1.fjs'
jobs, machines, products = commun_functions.transform_instance(file_path)

def generate_unique_coordinates(max_coordinate, existing_coordinates):
    while True:
        x = random.randint(0, max_coordinate)
        y = random.randint(0, max_coordinate)
        if (x, y) not in existing_coordinates:
            existing_coordinates.add((x, y))
            return x, y

def generate_cvrp_instance_from_schedule(schedule, products, vehicle_capacity, max_coordinate=100):
    depot = {'id': 1, 'x': random.randint(0, max_coordinate), 'y': random.randint(0, max_coordinate), 'demand': 0}
    clients = []
    existing_coordinates = {(depot['x'], depot['y'])}
    
    for item in schedule:
        product_id = item['product_id']
        quantity = item['quantity']
        x, y = generate_unique_coordinates(max_coordinate, existing_coordinates)
        clients.append({'id': product_id, 'x': x, 'y': y, 'demand': quantity})

    instance = {
        'depot': depot,
        'clients': clients,
        'vehicle_capacity': vehicle_capacity
    }

    return instance

def generate_orders_from_schedule(schedule, num_orders):
    orders = []
    for _ in range(num_orders):
        item = random.choice(schedule)
        order = {
            'client_id': item['product_id'],
            'product_id': item['product_id'],
            'quantity': item['quantity']
        }
        orders.append(order)
    return orders

def calculate_distance(client1, client2):
    return math.sqrt((client1['x'] - client2['x'])**2 + (client1['y'] - client2['y'])**2)

def create_distance_matrix(instance):
    depot = instance['depot']
    clients = instance['clients']
    nodes = [depot] + clients
    num_nodes = len(nodes)

    distance_matrix = [[0] * num_nodes for _ in range(num_nodes)]
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i != j:
                distance_matrix[i][j] = calculate_distance(nodes[i], nodes[j])

    return distance_matrix

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def calculate_vehicle_departure_times(schedule, best_routes):
    vehicle_departure_times = []
    for route in best_routes:
        latest_ready_time = 0
        for client in route:
            product_id = client['id']
            for machine_schedule in schedule:
                for item in machine_schedule:
                    if item[0] == product_id:
                        ready_time = item[3]  # End time of the operation
                        if ready_time > latest_ready_time:
                            latest_ready_time = ready_time
        vehicle_departure_times.append(latest_ready_time)
    return vehicle_departure_times



def main():
    data_instance = {
        'jobs': jobs,
        'machines': machines,
        'products': products
    }

    with ThreadPoolExecutor() as executor:
        stock_agent = StockAgent(products)

        scheduling_start_time = datetime.now()
        logging.info(f"Sheduling_start_time: {scheduling_start_time}")
        scheduling_future = executor.submit(test_RS, file_path)
        result = scheduling_future.result()
        scheduling_end_time = datetime.now()
        logging.info(f"Scheduling_end_time: {scheduling_end_time}")
        
        if result is None:
            logging.error("No result returned from test_RS")
            return

        best_solution, best_energy, total_execution_time, nm, nj, cmax, schedule, maint, ehf = result

        stock_agent.update_stock(schedule)
        updated_stock = stock_agent.stock

        updated_stock_by_jobs = stock_agent.aggregate_stock_by_jobs()

        vehicle_capacity = 10
        cvrp_instance = generate_cvrp_instance_from_schedule(updated_stock_by_jobs, products, vehicle_capacity)

        distance_matrix = create_distance_matrix(cvrp_instance)
        cvrp_instance['distance_matrix'] = distance_matrix

        num_orders = len(updated_stock_by_jobs)
        orders = generate_orders_from_schedule(updated_stock_by_jobs, num_orders)

        logging.info("CVRP Instance: %s", json.dumps(cvrp_instance, indent=4))
        logging.info("Orders: %s", json.dumps(orders, indent=4))

        routing_start_time = datetime.now()
        logging.info(f"Routing_start_time: {routing_start_time}")
        routing_agent = RoutingAgent(cvrp_instance, orders, stock_agent)
        routing_future = executor.submit(routing_agent.optimize_routes)
        best_routes = routing_future.result()
        routing_end_time = datetime.now()
        logging.info(f"Routing_end_time: {routing_end_time}")

        logging.info("Best Schedule Solution: %s", best_solution)
        logging.info("Updated Stock: %s", updated_stock)
        logging.info("updated_stock_by_jobs: %s", updated_stock_by_jobs)
        logging.info("Best Routes: %s", best_routes)

        # Calculate vehicle departure times
        vehicle_departure_times = calculate_vehicle_departure_times(schedule, best_routes)

        # Plot the Gantt chart
        plt.figure()
        gantt_chart = diagram(nm, nj, 2, 0.8, 0.1, cmax, schedule, maint, ehf, "final_best_solution", 1, 1)
        gantt_chart.plotGantt()
        gantt_chart.plotEHF2()

        # Plot the CVRP routes
        cvrp_functions.plot_cvrp_routes(cvrp_instance, best_routes, vehicle_departure_times)

        plt.show()

if __name__ == "__main__":
    main()
