import random
from opt_sim_module.solve import *

def findBest(pop):
	best = ['1', -0.0000001]
	for i in pop:
		if best[1] < pop[i].fitness:
			best = [i, pop[i].fitness]
	return best 

def findWorse(pop):
	worse = ['1', 9999999]
	for i in pop:
		if worse[1] > pop[i].fitness:
			worse = [i, pop[i].fitness]
	return worse

def initialize(pop, chromNodes, chromRange):
	for i in pop:
		chromList = []
		for j in range(chromNodes):
			chromList.append(random.uniform(chromRange[j][0], chromRange[j][1]+1))
		pop[i].chrom = chromList.copy()
	return pop

def calsumFitness(pop, N):
	sumFitness = 0
	for i in pop:
		sumFitness = sumFitness + pop[i].fitness
	return sumFitness



def mutChrom(pop, mut, chromNodes, bestChrom, chromRange):
	for i in pop:
		if mut > random.random():
			mutNode = random.randrange(0, chromNodes)
			mutRange = random.random() * (1 - pop[i].fitness/bestChrom[1])**2
			if random.random() > 0.5:
				pop[i].chrom[mutNode] = pop[i].chrom[mutNode] + (chromRange[mutNode][1] - pop[i].chrom[mutNode]) * mutRange
			else:
				pop[i].chrom[mutNode] = pop[i].chrom[mutNode] - (pop[i].chrom[mutNode] - chromRange[mutNode][0]) * mutRange
	return pop


def acrChrom(pop, acr, chromNodes):
	for i in pop:
		for j in pop:
			if acr > random.random():
				acrNode = random.randrange(0, chromNodes)
				pop[i].chrom[acrNode], pop[j].chrom[acrNode] = pop[j].chrom[acrNode], pop[i].chrom[acrNode]
	return pop


def compareChrom(nowbestChrom, bestChrom):
	if bestChrom[1]  > nowbestChrom[1]:
		return bestChrom
	else:
		return nowbestChrom

























