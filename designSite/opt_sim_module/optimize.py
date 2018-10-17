# -*- coding: utf-8 -*-
import opt_sim_module.Genetic as Genetic
import numpy as np
import math
from opt_sim_module.solve import *

def optimization(data, target, k, evol_t, ith_protein):
	class Chrom:
		chrom = []
		fitness = 0.0
		def showChrom(self):
			print(self.chrom)
		def showFitness(self):
			print(self.fitness)


	def calFitness(pop):
		for i in pop:
			pop[i].fitness = funcFitness(pop[i].chrom)
		return pop

	def funcFitness(chrom):
		fitness = 0.0
		time, result = solve_ode(data, chrom, evol_t)
		fitness = (target - result[:,ith_protein][-1])**2
		return 1.0 / fitness


	N = 100
	mut = 0.7
	acr = 0

	pop = {}
	for i in range(N):
		pop['chrom'+str(i)] = Chrom()
	chromNodes = len(k)#amount of variable
	iterNum = 200
	#the range of the chrom
	chromRange = []
	for i in range(len(k)):
		chromRange.append([0,100])
	bestFitnessList = []

	pop = Genetic.initialize(pop, chromNodes, chromRange)
	pop = calFitness(pop)  #计算适应度
	bestChrom = Genetic.findBest(pop)  #寻找最优染色体
	bestFitnessList.append(bestChrom)  #将当前最优适应度压入列表中


	for it in range(iterNum):
		pop = Genetic.mutChrom(pop, mut, chromNodes, bestChrom, chromRange)
		pop = Genetic.acrChrom(pop, acr, chromNodes)
		pop = calFitness(pop)
		nowBestChrom = Genetic.findBest(pop)
		bestChrom = Genetic.compareChrom(nowBestChrom, bestChrom)
		# 输出当前最佳适应度
		# 前面是那几个参数是目前最优的k 后面的那个是 对应的适应度有多少 一般来说 适应度大于1就算比较好的
		# print(pop[bestChrom[0]].chrom, pop[bestChrom[0]].fitness)
		if (pop[bestChrom[0]].fitness > 10):
			break
		worseChrom = Genetic.findWorse(pop)
		pop[worseChrom[0]].chrom = pop[bestChrom[0]].chrom.copy()
		pop[worseChrom[0]].fitness = pop[bestChrom[0]].fitness
		bestFitnessList.append(bestChrom)

	return pop[bestChrom[0]].chrom
	# print(Genetic.findBest(pop))
	# print(pop[Genetic.findBest(pop)[0]].chrom)
