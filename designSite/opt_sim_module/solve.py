# import matplotlib.pyplot as plt
import numpy as np
# from mpl_toolkits.mplot3d import Axes3D
from scipy import cos, linspace, pi, sin
from scipy.integrate import odeint, solve_bvp, solve_ivp


def solve_ode(data, k, evol_t):

	n = len(data['matrix'])

	def fvdp(y,t):
		Dy = []
		for i in range(n):
			inhibition = 1.0
			promotion = 0.0

			#inhitbition & promotion
			for j in range(n):
				if data['matrix'][i][j] == 1:
					promotion += y[j]
				elif data['matrix'][i][j] == 0:
					continue
				else:
					inhibition *= (1.0/(1 + y[j]**data['n'][j]))
			dy = k[i] * (promotion * inhibition) - data['d'][i] * y[i]

			#combine

			Dy.append(dy)

		return np.array(Dy)


	t = linspace(0,evol_t,1000)
	y0 = data['initial_value'] # 初值条件
	
	y_ = odeint(fvdp,y0,t)
	return t, y_
	"""
	plt.plot(y_.t, y_.y[0,:],'g--',label='y(0)')

    plt.show()
    """
