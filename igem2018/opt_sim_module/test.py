from opt_sim_module.solve import *
from optimize import *
import pandas as pd

data = {
	'matrix': [[0,0,0],[-1,0,0],[0,-1,0]],
	'initial_value': [50,0,6.944893725],
	'd': [0,0.15049821219066895, 0.11919929138025312],
	'n': [1.864112956487184,0.23470210357841204,0]
}

k = [0, 0, 3.0053138982435925]#k值
evol_t = 11 #演化时间


# data = {
# 	'matrix': [[0, 0, 0],[0, -1, 0], [-1, 0, 0]],
# 	'initial_value': [50, 6.944893725, 0],
# 	'd': [0, 0.11919929138025312, 0.15049821219066895],
# 	'n': [1.864112956487184,0,0.23470210357841204]
# }
# k = [0, 3.0053138982435925, 0]#k值
# evol_t = 11 #演化时间

#-------------------------------------
#仿真使用方法
'''
将上面数据传进函数solve_ode,返回结果，其中t为时间，y为演化量
其中y[:,0]为第1种物质的量的演化，y[:,1]为第2种，以此类推
'''
# t, y = solve_ode(data, k, evol_t)
# #画图
# plt.plot(t, y[:,1])
# plt.show()
#-------------------------------------

# y = np.array(pd.read_csv('data1.csv')['5mM psicose'])/1000000
# print(y[-1])




#-------------------------------------
#优化使用方法
'''
传进函数的你想要在演化时间使第i个物质(由0开始计数)达到的目标量，
返回优化的参数k
'''
ith_protein = 2
k_op = optimization(data,20.222, k, evol_t, ith_protein)
print(k_op)
# target = 20222679.07/1000000

# k_op = optimization(data, target, k, evol_t)
# print(k_op)
t1 = linspace(0,evol_t,67)
# #可以在优化的参数下观察现在物质的量的演化
t, y_ = solve_ode(data, k_op, evol_t)
# plt.plot(t1,y)

# plt.plot(t, y_[:,2])

# plt.show()
#-------------------------------------