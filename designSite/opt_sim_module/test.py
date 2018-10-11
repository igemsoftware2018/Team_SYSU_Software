from solve import *
from optimize import *

data = {
	'matrix': [[0,1],[1,0]],
	'initial_value': [1,0],
	'd': [1,1],
	'n': [1,1]
}

k = [0.13266746665830317,8.949699559416413] #k值
eval_t = 10 #演化时间


#-------------------------------------
#仿真使用方法
'''
将上面数据传进函数solve_ode,返回结果，其中t为时间，y为演化量
其中y[:,0]为第1种物质的量的演化，y[:,1]为第2种，以此类推
'''
t, y = solve_ode(data, k, eval_t)
print(y)


#画图
# plt.plot(t, y[:,-1])
# plt.show()
#-------------------------------------


#-------------------------------------
#优化使用方法
'''
传进函数的你想要在演化时间使第i个物质(由0开始计数)达到的目标量，
返回优化的参数k
'''
# ith_protein = -1
# target = 10
# k_op = optimization(data, eval_t, target, k, ith_protein)
# print(k_op)

# #可以在优化的参数下观察现在物质的量的演化
# t, y = solve_ode(data, k_op, eval_t)

# plt.plot(t, y[:,ith_protein])
# plt.show()
#-------------------------------------