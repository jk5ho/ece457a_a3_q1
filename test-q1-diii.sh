#!/bin/bash

python3 q1.py 20 150 0.6 0.2 > log_population_20.txt

# Varying generations
for a in 100 200
do
    echo "Generation $a"
    python3 q1.py 50 $a 0.6 0.25 > log_generation_$a.txt
done

# Varying population sizes
for b in 20 100
do
    echo "Population $b"
    python3 q1.py $b 150 0.6 0.25 > log_population_$b.txt
done

# Varying crossover probability
for i in 0.4 0.5 0.7 0.8
do
    echo "Crossover $i"
    python3 q1.py 50 150 $i 0.25 > log_crossover_$i.txt
done

# Varying mutation probability
for j in 0.15 0.2 0.3 0.35
do
    echo "Mutation $j"
    python3 q1.py 50 150 0.6 $j > log_mutation_$j.txt
done
