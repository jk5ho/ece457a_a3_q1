from control import matlab

import control
import random
import math
import sys

# PID function to minimize
def Q1_perfFCN(Kp,Ti,Td):
    G = Kp * control.TransferFunction([Ti*Td,Ti,1],[Ti,0])
    F = control.TransferFunction([1], [1,6,11,6,0])
    sys = control.feedback(control.series(G,F),1)
    t = []
    for i in range(0,10001): 
        t.append(i/100)
    y,t = control.matlab.step(sys,t)
    
    ISE = 0
    t_r = 0
    t_s = 0
    M_p = (max(y) -1) * 100
    
    t_10_to_90 = 0
    for e,i in enumerate(y):
        ISE += (i-1) ** 2
        if i >=.1 and t_10_to_90 == 0:
            t_10_to_90 = e * 0.01
        if i >= 0.9 and t_r == 0:
            t_r = e * 0.01
    e = len(y)
    for i in reversed(y):
        if i < 0.98 or i > 1.02:
            t_s = (e-1) * 0.01
            break
        e-=1
    t_r -= t_10_to_90
    t_s = 100 - t_s

    return ISE,t_r,t_s,M_p

# Evaluate function
def evalute(ISE):
    return 1/ISE

# Converts number into binary representation
def bitMapping(min_val,max_val,n,val):
    precision = (max_val-min_val)/((2**n)-1)
    number = math.ceil((val-min_val)/precision)
    bit = bin(number).replace('0b','')
    return bit.zfill(n)

# Converts binary into base-10 number representation
def numMapping(bit, bit_size):
    Kp = int(bit[:bit_size],2)
    Ti = int(bit[bit_size:bit_size*2],2)
    Td = int(bit[bit_size*2:],2)

    p_kp = (18-2)/((2**bit_size)-1)
    p_ti = (9.42-1.05)/((2**bit_size)-1)
    p_td = (2.37-0.26)/((2**bit_size)-1)

    Kp = 2 + (Kp)*p_kp
    Ti = 1.05 + (Ti)*p_ti
    Td = .26 + (Td)*p_td

    return Kp,Ti,Td

# Crossover operation
def crossover(mom,dad,p_c,bit_size):
    child1 = mom
    child2 = dad
    prob = random.uniform(0.00,1.00)

    if prob <= p_c:
        point = random.randint(0,bit_size*3-1)
        child1 = dad[:point] + mom[point:]
        child2 = mom[:point] + dad[point:]
    return child1,child2

# Mutation operation
def mutation(child,p_m):
    temp = ''
    for i in range(len(child)):
        prob = random.uniform(0.00,1.00)
        if prob < p_m:
            if child[i] == '0':
                temp += '1'
            else:
                temp += '0'
        else:
            temp += child[i]
    return temp

# Genetic Algorithm
def main():

    # Tunable Parameters
    population  = int(sys.argv[1]) #50
    generations = int(sys.argv[2]) #150
    p_crossover = float(sys.argv[3]) #0.6
    p_mutation  = float(sys.argv[4]) #0.25

    bit_length = 20
    offspring = []
    for i in range(population):
        Kp = round(random.uniform(2.00,18.00),2)
        Ti = round(random.uniform(1.05, 9.42),2)
        Td = round(random.uniform(0.26, 2.37),2)
        offspring.append([Kp,Ti,Td])

    print("Population: ",population,", Generation: ",generations,", Crossover %: ",p_crossover,", Mutation %: ",p_mutation)
    iteration = 0
    while iteration < generations:
        max1 = -1
        max2 = -1
        max1_ind = 0
        max2_ind = 0

        # Evaluating Colony's fitness
        colony = []
        totalFitness = 0
        for e,i in enumerate(offspring):
            ISE,Tr,Ts,Mp = Q1_perfFCN(i[0],i[1],i[2])
            genotype = bitMapping(2.00,18.00,bit_length,i[0]) + bitMapping(1.05,9.42,bit_length,i[1]) + bitMapping(0.26,2.37,bit_length,i[2])
            fitness = evalute(ISE)
            totalFitness += fitness
            colony.append([genotype,fitness])

            if fitness > max1:
                max2_ind = max1_ind
                max1_ind = e
                max2 = max1
                max1 = fitness
            elif fitness > max2:
                max2_ind = e
                max2 = fitness

        # Elitism Survival Selection
        if max1_ind > max2_ind:
            elite1 = colony.pop(max1_ind)
            elite2 = colony.pop(max2_ind)
            bc1 = offspring.pop(max1_ind)
            bc2 = offspring.pop(max2_ind)
        else:
            elite2 = colony.pop(max2_ind)
            elite1 = colony.pop(max1_ind)
            bc2 = offspring.pop(max2_ind)
            bc1 = offspring.pop(max1_ind)

        # Fitness Propotional Selection
        pool = []
        totalFitness = totalFitness - elite1[1] - elite2[1]
        use = totalFitness
        for _ in range(population-2):
            threshold = random.uniform(0.00,use)
            cumulative = 0
            for i in colony:
                cumulative += i[1]/totalFitness
                if cumulative >= threshold:
                    use -= i[1]/totalFitness
                    pool.append(i[0])
                    colony.remove(i)
                    break

        # Offsprings - Crossover + Mutation
        offspring = []
        while pool:
            child1,child2 = crossover(pool.pop(),pool.pop(),p_crossover,bit_length)
            child1 = mutation(child1,p_mutation)
            child2 = mutation(child2,p_mutation)
            Kp_1, Ti_1, Td_1 = numMapping(child1,bit_length)
            Kp_2, Ti_2, Td_2 = numMapping(child2,bit_length)
            offspring.append([Kp_1,Ti_1,Td_1])
            offspring.append([Kp_2,Ti_2,Td_2])
        offspring.append(bc1)
        offspring.append(bc2)

        print("Iteration: ",iteration," --> ",elite1[0]," scoring ",elite1[1])
        iteration += 1

if __name__ == '__main__':
    main()
