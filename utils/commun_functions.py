import random
import numpy as np
import math 

def FJSInstanceReading(filepath):
      proctimes=[]
      with open(filepath, 'r') as f:
            line = f.readline().strip()
            values = line.split()
            NJ=int(values[0])
            NM=int(values[1])
            NOPmax=0
            NOP=[]
            NBRM=[]
            PRT=[]
            proctimes=[]
            for j in range(NJ):
                  line = f.readline().strip()
                  values = line.split()
                  if int(values[0])>NOPmax:
                        NOPmax=int(values[0])
                  NOP.append(int(values[0]))
                  #print("NOP(",j,")=",NOP[j])
                  NBRM_jii=0
                  NBRM.append([])
                  PRT.append([])
                  proctimes.append([])
                  for i in range(NOP[j]):
                        NBRM[j].append(int(values[i+1+NBRM_jii*2]))
                        PRT[j].append([])
                        proctimes[j].append([])
                        #print("NBRM_ji=",NBRM[j][i])
                        for k in range(NM):
                              PRT[j][i].append(0)
                        for k in range(NBRM[j][i]):
                              M_ID_jik=int(values[i+2+2*k+NBRM_jii*2])-1
                              PRT_ji_m =int(values[i+3+2*k+NBRM_jii*2])
                              #print("j=",j,", i=",i,", M_ID_",j,i,k,"=",M_ID_jik,",PRT_ji_m=",PRT_ji_m)
                              PRT[j][i][M_ID_jik] = PRT_ji_m
                              proctimes[j][i].append((M_ID_jik,PRT_ji_m))
                        NBRM_jii=NBRM_jii+NBRM[j][i]    
      return proctimes

def read_instance(instancefilename):
    with open(instancefilename, 'r') as f:
        line = f.readline().strip()
        values = line.split()
        NM=int(values[0])
        NJ=int(values[1])
        NOPmax=0
        NOP=[]
        NBRM=[]
        PRT=[]
        MU=[]
        LAMBDA=[]
        for j in range(NJ):
            line = f.readline().strip()
            values = line.split()
            if int(values[0])>NOPmax:
                NOPmax=int(values[0])
            NOP.append(int(values[0]))
            #print("NOP(",j,")=",NOP[j])
            NBRM_jii=0
            NBRM.append([])
            PRT.append([])
            for i in range(NOP[j]):
                NBRM[j].append(int(values[i+1+NBRM_jii*2]))
                PRT[j].append([])
                #print("NBRM_ji=",NBRM[j][i])
                for k in range(NM):
                    PRT[j][i].append(0)
                for k in range(NBRM[j][i]):
                    M_ID_jik=int(values[i+2+2*k+NBRM_jii*2])-1
                    PRT_ji_m =int(values[i+3+2*k+NBRM_jii*2])
                    PRT[j][i][M_ID_jik] = PRT_ji_m
                NBRM_jii=NBRM_jii+NBRM[j][i]    
        line = f.readline().strip()
        for m in range(NM):
            line = f.readline().strip()
            values = line.split()
            MU.append(float(values[0]))
            LAMBDA.append(float(values[1]))
    f.close()
    sumpmax=0
    for j in range(NJ):
        for i in range(NOP[j]):
            pmax = 0.0
            for k in range(NM):
                if float(PRT[j][i][k]) > pmax:
                    pmax = PRT[j][i][k]
            sumpmax += pmax
    NP = math.ceil(sumpmax)
    
    return PRT

def evaluate(Solution, data):
    """
    This function evaluates the objective value of 'Solution'.

    Args:
        Solution: the solution to be evaluated
        data: an object of type data that gathers all the data of the current instance

    Returns:
        NM: Number of machines
        NJ: Number of jobs
        cmax: the makespan
        schedule: list of tasks executed on each machine with their start and end dates
        maint: list of maintenance tasks scheduled for each machine
        ehf: the degradation status of each machine at each instant t
        uava: list of unavailability periods for each machine
    """
    NM = len(data['machines'])
    NJ = len(data['jobs'])

    ehf = [0 for _ in range(NM)]
    uava = [0 for _ in range(NM)] 
    maint = [[] for _ in range(NM)]
    operid = [0 for _ in range(NJ)]
    schedule = [[] for _ in range(NM)]

    for task in Solution:
        jobid = task['job_id']
        operation_id = task['operation_id']
        machineid = task['machine_id'] - 1
        
        # Trouver le temps de traitement
        job = next(job for job in data['jobs'] if job['id'] == jobid)
        operation = next(op for op in job['operations'] if op['id'] == operation_id)
        
        # Check if machine_id exists in processing_times
        if task['machine_id'] not in operation['processing_times']:
            raise KeyError(f"Machine ID {task['machine_id']} not found in processing times for job {jobid}, operation {operation_id}")

        pt = operation['processing_times'][task['machine_id']]

        ehf[machineid] = round(ehf[machineid] + data['machines'][machineid]['mu'] * pt, 3)
        
        if len(schedule[machineid]) > 0:
            tstart = schedule[machineid][-1][3]
            if ehf[machineid] > data['machines'][machineid]['lambda']:
                uava[machineid] += data['machines'][machineid]['PM_time']
                maint[machineid].append((tstart, uava[machineid]))
                ehf[machineid] = round(data['machines'][machineid]['mu'] * pt, 3)
                tstart += data['machines'][machineid]['PM_time']
        else:
            tstart = 0

        endtimeprevious = 0
        if operid[jobid - 1] > 0:
            previous_operations = [
                schedule[m][-1][3] for m in range(NM)
                if schedule[m] and schedule[m][-1][0] == jobid and schedule[m][-1][1] == operid[jobid - 1] - 1
            ]
            if previous_operations:
                endtimeprevious = max(previous_operations)
        
        if endtimeprevious > tstart:
            tstart = endtimeprevious
        endtime = tstart + pt                  
        schedule[machineid].append((jobid, operid[jobid - 1], tstart, endtime))
        operid[jobid - 1] += 1
    
    # Debugging: print the evaluated schedule
    #print("Evaluated Schedule:", schedule)
    
    cmax = int(max([schedule[m][-1][3] for m in range(NM) if schedule[m]]))

    return NM, NJ, cmax, schedule, maint, ehf



def Voisinage(Solution_,LargV,NbrV,data): 
    Solution = Solution_[:]
    voisins = []
    while len(voisins) < NbrV:
        nbropersfound = 0
        SelectOper = []
        while nbropersfound < LargV:
            nbropersfound = 0
            SelectOper = np.sort(random.sample(range(len(Solution)), LargV))
            for tid, opid in enumerate(SelectOper):
                jobid = Solution[opid][0]
                machid = Solution[opid][1]
                operid = sum([Solution[i][0] == jobid for i in range(opid)])
                if len([omid[0] for id, omid in enumerate(data.ProcTime[jobid][operid]) if omid[0] != machid]) > 0:
                    nbropersfound += 1
        voisin = Solution_[:]
        for tid, opid in enumerate(SelectOper):
            jobid = Solution[opid][0]
            machid = Solution[opid][1]
            operid = sum([Solution[i][0] == jobid for i in range(opid)])
            compmach = [omid[0] for omid in data.ProcTime[jobid][operid] if omid[0] != machid]
            if len(compmach) > 0:
                selectmach = random.choice(compmach)
                listvoisin = list(voisin[opid])
                listvoisin[1] = selectmach
                voisin[opid] = tuple(listvoisin)
        if voisin != Solution and voisin not in voisins:
            voisins.append(voisin)    
    return voisins

def Voisinage2(Solution,LargV,NbrV,PTimes): 
    voisins = []
    while len(voisins) < NbrV:
        voisin = []
        selected_opers_sample = random.sample(range(len(Solution)), k=LargV)
        selected_opers_sorted = sorted(selected_opers_sample)
        selected_opers_sample = sorted(selected_opers_sample)
        if LargV > 1:
            while sum([selected_opers_sorted[i] == selected_opers_sample[i] for i in range(LargV)]) > 0:
                random.shuffle(selected_opers_sample)
        nbr = 0
        for i, sol in enumerate(Solution):
            jobid = sol[0]
            machid0 = sol[1]
            if nbr < LargV:
                if i == selected_opers_sorted[nbr]:
                    sol0 = Solution[selected_opers_sample[nbr]]
                    voisin.append(sol0)
                    nbr += 1
                else:
                    voisin.append(sol)
            else:
                voisin.append(sol)
        partvoisin = []
        for i, sol in enumerate(voisin):
            partvoisin.append(sol)
            jid = sol[0]
            opid = sum([s[0] == jid for si, s in enumerate(partvoisin)]) - 1
            compmach = [om[0] for ji, job in enumerate(PTimes) for oi, o in enumerate(job) for omi, om in enumerate(o) if ji == jid and oi == opid]
            if sol[1] not in compmach:
                newm = random.choice(compmach)
                sol = (jid, newm)
            else:
                if len(compmach) > 0:
                    newm = random.choice(compmach)
                    sol = (jid, newm)
        voisins.append(voisin)
    return voisins


# Nouvelle implémentation de GenererSolution pour utiliser les nouvelles structures de données
def GenererSolution(data):
    """
    A function that generates a random solution.

    Args:
        data: an instance

    Returns:
        Solution: a randomly constructed solution.
    """
    Solution = []
    opers = []
    for job in data['jobs']:
        for op in job['operations']:
            opers.append((job['id'], op['id']))
    random.shuffle(opers)
    for job_id, oper_id in opers:
        job = next(job for job in data['jobs'] if job['id'] == job_id)
        operation = next(op for op in job['operations'] if op['id'] == oper_id)
        valid_machines = [mach for mach in operation['machines'] if mach in operation['processing_times']]
        if not valid_machines:
            raise KeyError(f"No valid machines found in processing times for job {job_id}, operation {oper_id}")
        select_mach = random.choice(valid_machines)
        Solution.append({'job_id': job_id, 'operation_id': oper_id, 'machine_id': select_mach})
    
    # Debugging: print the generated solution
    #print("Generated initial solution:", Solution)
    return Solution



# Nouvelle implémentation de VoisinageAll pour utiliser les nouvelles structures de données
def VoisinageAll(Solution, data):
    """ Cette fonction permet de générer toutes les solutions voisines d'un point 

    Args:
        Solution: The solution in question
        data: an instance

    Returns:
        voisins: list of neighbors
    """
    voisins = []
    for id, i in enumerate(Solution):
        for jid, j in enumerate(Solution):
            if jid > id:
                voisin = Solution[:]
                op1 = i.copy()
                op2 = j.copy()
                if op1['job_id'] != op2['job_id'] or op1['machine_id'] != op2['machine_id']:
                    temp_job = op1['job_id']
                    op1['job_id'] = op2['job_id']
                    op2['job_id'] = temp_job
                    
                    # Get job and operation indices
                    job1_index = op1['job_id'] - 1
                    op1_index = op1['operation_id'] - 1
                    job2_index = op2['job_id'] - 1
                    op2_index = op2['operation_id'] - 1
                    
                    # Verify if indices are within bounds
                    if job1_index < 0 or job1_index >= len(data['jobs']):
                        continue
                    if job2_index < 0 or job2_index >= len(data['jobs']):
                        continue
                    if op1_index < 0 or op1_index >= len(data['jobs'][job1_index]['operations']):
                        continue
                    if op2_index < 0 or op2_index >= len(data['jobs'][job2_index]['operations']):
                        continue

                    # Verify if the machine IDs are valid for the operations
                    valid_op1_machines = data['jobs'][job1_index]['operations'][op1_index]['processing_times']
                    valid_op2_machines = data['jobs'][job2_index]['operations'][op2_index]['processing_times']
                    
                    if op1['machine_id'] not in valid_op1_machines:
                        continue
                    if op2['machine_id'] not in valid_op2_machines:
                        continue
                    
                    voisin[id] = op1
                    voisin[jid] = op2
                    voisins.append(voisin)
    
    #print("Generated neighbors:", voisins)
    return voisins


def transform_instance(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Lecture de la première ligne pour le nombre de jobs et de machines
    first_line = lines[0].strip().split()
    num_jobs = int(first_line[0])
    num_machines = int(first_line[1])
    # additional_value = float(first_line[2])  # Si nécessaire

    jobs = []
    index = 1
    for job_id in range(1, num_jobs + 1):
        job_line = lines[index].strip().split()
        num_operations = int(job_line[0])
        operations = []
        i = 1
        for op_id in range(1, num_operations + 1):
            num_machines_for_op = int(job_line[i])
            machines = []
            processing_times = {}
            i += 1
            for _ in range(num_machines_for_op):
                machine = int(job_line[i])
                processing_time = int(job_line[i + 1])
                machines.append(machine)
                processing_times[machine] = processing_time
                i += 2
            operations.append({'id': op_id, 'machines': machines, 'processing_times': processing_times})
        jobs.append({'id': job_id, 'operations': operations})
        index += 1

    machines = [{'id': i, 'capacity': 10, 'lambda': 0.01, 'mu': 0.1, 'PM_time': 5} for i in range(1, num_machines + 1)]

    # Génération de la liste des produits
    products = [{'id': job_id, 'capacity': 20, 'job_id': job_id} for job_id in range(1, num_jobs + 1)]

    return jobs, machines, products






