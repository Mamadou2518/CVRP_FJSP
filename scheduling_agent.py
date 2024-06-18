import random
import math
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from utils import commun_functions, diagram, data

class SchedulingAgent:
    def __init__(self, initial_solution, data):
        self.initial_solution = initial_solution
        self.data = data
        self.execution_time = 0

    def CritMetropolis(self, delta, temperature):
        if delta <= 0:
            return True
        else:
            if random.random() < math.exp((-1 * delta) / temperature):
                return True
            return False

    def simulated_annealing(self, initial_temperature, cooling_rate, stopping_temperature, size_iteration):
        t0 = time.perf_counter()
        current_solution = self.initial_solution
        current_energy = commun_functions.evaluate(current_solution, self.data)[2]
        best_solution = current_solution
        best_energy = current_energy
        temperature = initial_temperature

        iteration = 0
        while temperature > stopping_temperature:
            logging.info(f"Iteration {iteration}, Temperature {temperature}, Current Energy {current_energy}, Best Energy {best_energy}")
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.evaluate_neighbor, current_solution) for _ in range(size_iteration)]
                for future in futures:
                    neighbor_solution, neighbor_energy = future.result()
                    delta = neighbor_energy - current_energy
                    if self.CritMetropolis(delta, temperature):
                        current_solution = neighbor_solution
                        current_energy = neighbor_energy

                    if current_energy < best_energy:
                        best_solution = current_solution
                        best_energy = current_energy

            temperature *= cooling_rate
            iteration += 1

        t1 = time.perf_counter()
        self.execution_time = t1 - t0
        return best_solution, best_energy, iteration

    def evaluate_neighbor(self, current_solution):
        neighbor_solution = commun_functions.VoisinageAll(current_solution, self.data)
        best_voisin = []
        best_voisin_energy = float('inf')

        for voisin in neighbor_solution:
            try:
                energy = commun_functions.evaluate(voisin, self.data)[2]
                if best_voisin_energy > energy:
                    best_voisin = voisin
                    best_voisin_energy = energy
            except KeyError as e:
                logging.error(f"KeyError: {e}")

        return best_voisin, best_voisin_energy

def call_RS(data_instance):
    best_solution = []
    best_energy = float('inf')

    t0 = time.perf_counter()
    temperature_initial = [50, 70]
    temperature_final = [0.1, 0.2]
    cooling_rate = [0.01, 0.02]
    iterations = [50, 100]

    total_execution_time = 0 
    for i in range(4):
        for tpi in temperature_initial:
            for tpf in temperature_final:
                for cr in cooling_rate: 
                    for it in iterations:
                        ti = time.perf_counter()
                        if ti - t0 <= 120:
                            initial_solution = commun_functions.GenererSolution(data_instance)
                            scheduling_agent = SchedulingAgent(initial_solution, data_instance)
                            solution, energy, nb_iteration = scheduling_agent.simulated_annealing(tpi, cr, tpf, it)

                            if energy < best_energy:
                                best_energy = energy
                                best_solution = solution
                                total_execution_time += scheduling_agent.execution_time
                        else: 
                            return best_solution, best_energy, total_execution_time
                            
    return best_solution, best_energy, total_execution_time

def test_RS(instancefilename):
    lambdaPM = [0.8]
    mu = [0.1]
    PM_time = [2]

    print("lambda 	Mu	PM_time	Cmax	nb PM	Execution (s)")
    for lbd in lambdaPM:
        for m in mu: 
            for pm in PM_time: 
                jobs, machines, products = commun_functions.transform_instance(instancefilename)
                for machine in machines:
                    machine['lambda'] = lbd
                    machine['mu'] = m
                    machine['PM_time'] = pm

                data_instance = {
                    'jobs': jobs,
                    'machines': machines,
                    'products': products
                }

                best_solution, best_energy, total_execution_time = call_RS(data_instance)
                nm, nj, cmax, schedule, maint, ehf = commun_functions.evaluate(best_solution, data_instance)
                nb_PM = sum([len(m) for m in maint])

                print(f"{lbd}   {m} {pm}    {cmax}   {nb_PM} {total_execution_time}")

                return best_solution, best_energy, total_execution_time, nm, nj, cmax, schedule, maint, ehf

