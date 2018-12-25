##
#	plots the residual command curves and the new offer stack
#

from pulp import *
#from gurobipy import *
from math import *
import offer_stack as offer_stack
#import matplotlib.pyplot as plt
import numpy as np
#from mpl_toolkits.mplot3d import axes3d

def main():

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	X, Y, Z = axes3d.get_test_data(0.05)

	ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)

	plt.show()

def plot3D(p_t, q_t, q_t2):
	fig = plt.figure()
	ax = fig.add_subplot(111, projection = '3d')

	ax.plot(q_t, q_t2, p_t)

	ax.set_xlabel('q_t')
	ax.set_ylabel('q_t2')
	ax.set_zlabel('p_t')

	plt.show()




def plotsinglefull(p_t, y, price, quantity, demands, tranches, 
					graph_title1, graph_title2, file_name1,  file_name2,
					x_label = 'Strategic Offer (MW)', y_label = 'Price ($)',
					file_ext = 'pdf',
					xlim_on = 0, ylim_on = 0):
	'''
	Plots the residual demand curve, points of intersection and
	intersecting curve
	'''
	# Plots residual demand curve
	plotrdc(price, quantity, demands, tranches)



	# Plots optimal points
	plt.plot(y,p_t, marker = 'o', ls = ' ')
	
	# plt.grid(True, which="major", axis='both', ls="-")
	plt.grid(True, which="both")
	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.title(graph_title1)


	if xlim_on and ylim_on:
		plt.ylim((0,ylim_on))
		plt.xlim((0,xlim_on))
	# else:
		# plt.ylim((0,400))
		# plt.xlim((0,4500))

	plt.savefig('%s.png' %file_name1, dpi = 300)

	plt.draw()

	# Plots resulting offer stack on seperate plot
	plt.figure()

	plt.grid(True, which="both")
	plt.title(graph_title2)
	plt.xlabel(x_label)
	plt.ylabel(y_label)

	if xlim_on and ylim_on:
		plt.ylim((0,ylim_on))
		plt.xlim((0,xlim_on))
	# else:
		# plt.ylim((0,400))
		# plt.xlim((0,4500))

	p_t.sort()
	y.sort()	

	plot_offer_stack(p_t,y)

	plt.savefig('%s.png'%file_name2, dpi = 300)

	plt.show()

def plottranchelevels(p_t,y, graph_title,
						x_label = 'Strategic Offer (MW)', y_label = 'Price ($)', 
						xlim_on = 0, ylim_on = 0, file_name = "Tranche_Example"):

	p_t.sort()
	y.sort()

	# Plots optimal points
	plt.plot(y,p_t, marker = 'o', color = 'r', ls = ' ')

	labels = [i+1 for i in range(len(y))]

	for i in range(len(y)):
		plt.text(y[i], p_t[i], i+1, fontsize=18, horizontalalignment='left',verticalalignment='top',linespacing=4)

	(y_level, x_level) = findtranchelevels(p_t,y)
	
	# plt.grid(True, which="major", axis='both', ls="-")
	plt.gca().set_yticks(y_level, minor=True)
	plt.gca().set_xticks(x_level, minor=True)
	plt.grid(True, which="minor", ls = "-")
	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.title(graph_title)


	if xlim_on and ylim_on:
		plt.ylim((0,ylim_on))
		plt.xlim((0,xlim_on))

	plt.savefig('%s.pdf' %file_name)

	plt.show()

def findtranchelevels(p_t,y):
	tol = 0.1

	n_d = range(len(p_t))

	x_level = [y[0]]
	y_level = [p_t[0]]

	p_t.insert(0,p_t[0])
	p_t.append(1000)
	
	y.insert(0,0)
	y.append(y[-1])
	

	switch = 1

	for i in range(0,len(p_t)-1):
		if (abs(p_t[i+1] - p_t[i]) > tol) & (abs(y[i+1] - y[i]) > tol):
			if switch == 0:
				y_level.append(p_t[i+1])
				x_level.append(y[i+1])
				
			else:
				y_level.append(p_t[i+1])
				x_level.append(y[i+1])

			switch = 1 - switch

	return (y_level, x_level)
	

def plotmultifull(tranch, price, quantity, 
					demands,nodes, M,
					p_t, y, arcs, flow1 = 0,
					x_label = "Strategic Offer(MW)", y_label = "Offer Price($)",
					graph_title = "Plot of Optimal Points",
					file_ext = 'pdf',
					file_name = "Optimal_Points", xlim_on=120, ylim_on=200):

	n_d = range(len(demands))
	# Split tranch data by node

	prices = {}
	quantities = {}
	tranches = {}

	for p in n_d:

		(tranches[p], prices[p], quantities[p]) = offer_stack.SplitDataByNode(nodes, tranch,
	                                                   price[p], quantity[p], M)
		tranches[p] = dict(zip( nodes, tranches[p] ))
		prices[p] = dict(zip( nodes, prices[p] ))
		quantities[p] = dict(zip( nodes, quantities[p] ))



	for n in nodes:
		# plt.figure()

		# plot_prices = [prices[p][n] for p in n_d]
		# plot_quantities = [quantities[p][n] for p in n_d]
		# plot_demands = [demands[p][n] for p in n_d]

		# # for a in arcs:
		# # 	if n == i:
		# # 		plot_demands = [demands[p][n] + flow1[i,j][p] - flow2[i,j][p] for p in n_d]
		# # 	elif n ==j:
		# # 		plot_demands = [demands[p][n] - flow1[i,j][p] + flow2[i,j][p] for p in n_d]


		# plot_tranches = [tranches[p][n] for p in n_d]
		
		# plotrdc(plot_prices, plot_quantities, plot_demands, plot_tranches)

		# plt.xlabel(x_label + " at %s" %n)
		# plt.ylabel(y_label + " at %s" %n)
		# plt.title(graph_title + " at %s" %n)

		# if xlim_on:
		# 	plt.xlim((0,xlim_on))
		# if ylim_on:
		# 	plt.ylim((0,ylim_on))

		# plt.grid(True, which="major", axis='both', ls="--")

		# plt.grid(True, which = "minor", axis = 'both', ls=".")

		

		# for i in n_d:
		# 	plt.text(y[n][i], p_t[n][i], i+1, fontsize=15, horizontalalignment='left',verticalalignment='top', linespacing=3)



		# plt.plot(y[n],p_t[n], marker = 'o', color = 'r', ls = ' ')

		# plt.savefig('Optimal_Points'+'_%s.pdf' % n)

		plt.figure()

		# for i in n_d:
		# 	plt.text(y[n][i], p_t[n][i], i+1, fontsize=15, horizontalalignment='left',verticalalignment='top', linespacing=3)

		plt.plot(y[n], p_t[n], marker = 'o', ls = ' ')

		p_t[n].sort()
		y[n].sort()

		plot_offer_stack(p_t[n], y[n])

		plt.xlabel(x_label + " at %s" %n)
		plt.ylabel(y_label + " at %s" %n)
		plt.title(graph_title + " at %s" %n)

		if xlim_on:
			plt.xlim((0,xlim_on))
		if ylim_on:
			plt.ylim((0,ylim_on))

		plt.grid(True, which="major", axis='both', ls="--")

		plt.grid(True, which = "minor", axis = 'both', ls=".")

		plt.savefig('Offer_Stack'+'_%s.png' % n, dpi = 300)

	

	plt.draw()

def plotmultistack(tranch, price, quantity,
					demands,nodes, M,
					p_t, y, flow1 = 0, stack_no = 0,
					x_label = "Strategic Offer(MW)", y_label = "Offer Price($)",
					graph_title = "Plot of Optimal Points",
					file_ext = 'png',
					file_name = "Optimal_Points", xlim_on=120, ylim_on=200):

	n_d = range(len(demands))
	# Split tranch data by node
	prices = {}
	quantities = {}
	tranches = {}

	for p in n_d:

		(tranches[p], prices[p], quantities[p]) = offer_stack.SplitDataByNode(nodes, tranch,
	                                                   price[p], quantity[p], M)
		tranches[p] = dict(zip( nodes, tranches[p] ))
		prices[p] = dict(zip( nodes, prices[p] ))
		quantities[p] = dict(zip( nodes, quantities[p] ))

        c=['b','r','g']
        mark=['s','^','o']
        label=['0','inf','50']
	for n in nodes:

		plt.figure()
		for i in range(stack_no):

			

			# for j in n_d:
			# 	plt.text(y[i][n][j], p_t[i][n][j], j+1, fontsize=15, horizontalalignment='left',verticalalignment='top', linespacing=3)

			# plt.plot(y[i][n], p_t[i][n], marker = 'o', color = 'r', ls = ' ')

			p_t[i][n].sort()
			y[i][n].sort()
			plot_offer_stack(p_t[i][n], y[i][n],c[i],mark[i],label[i])

		plt.xlabel(x_label + " at %s" %n)
		plt.ylabel(y_label + " at %s" %n)
		plt.title(graph_title + " at %s" %n)

		if xlim_on:
			plt.xlim((0,xlim_on))
		if ylim_on:
			plt.ylim((0,ylim_on))

		plt.grid(True, which="major", axis='both', ls="--")

		plt.grid(True, which = "minor", axis = 'both', ls=".")
                plt.legend()
		plt.savefig('Offer_Stack'+'_%s_%d.png' % (n,stack_no), format='png')

	plt.draw()


def plotmultirdc(tranches, price, quantity, demands, strategic_nodes, M, p_t, q_t):
	for i in strategic_nodes:
		plt.figure()
		plt.plot(q_t[i],p_t[i], marker = 'o', color = 'r', ls = ' ')
		plt.draw()

	plt.show()




def plotrdc(price, quantity, demands, tranches):
	'''
	Plots the residual demand curve
	'''
	n_d = range(len(demands))

	price_points = []
	quantity_points = []

	# Residual demand points
	for i in n_d:
		n_pq = range(len(price[i]))

		sort_list = zip(price[i], tranches[i], quantity[i])
		list.sort(sort_list)
		(price[i], tranches[i], quantity[i]) = zip(*sort_list)

		price_points.append([])
		quantity_points.append([])

		price_points[i] = [p for p1 in price[i] for p in [p1]*2]
		del price_points[i][-1]
		price_points[i].insert(0,0)

		quantity_cml = [sum(quantity[i][0:q]) for q in n_pq]
		quantity_points[i] = [q for q1 in quantity_cml for q in [q1]*2]

	rd = []
	for i in n_d:
		rd.append([])
		rd[i] = [demands[i] - y for y in quantity_points[i]]

	for i in n_d:
		plt.plot( rd[i], price_points[i])


def plot_offer_stack(p_t, y, c='r', mark='o', l='test'):
	'''
	Plots the intersection offer stack
	'''
	n_d = range(len(p_t))

	# Line of intersection points

	(p,y) = create_tranch_points(p_t, y)

	p.append(500)
	y.append(y[-1])

	plt.plot(y,p, lw = 2, ls = '-', color = c, marker = mark, label = l)

	plt.draw()


def create_tranch_points(p_t, y):
	tol = 0.1

	n_d = range(len(p_t))

	p_t.insert(0,p_t[0])
	p_t.append(10000)
	p_points = []
	
	y.insert(0,0)
	y.append(y[-1])
	y_points = []

	switch = 1

	for i in range(0,len(p_t)-1):
		p_points.append(p_t[i])
		y_points.append(y[i])
		if (abs(p_t[i+1] - p_t[i]) > tol) & (abs(y[i+1] - y[i]) > tol):
			if switch == 0:
				p_points.append(p_t[i+1])
				y_points.append(y[i])
				
			else:
				p_points.append(p_t[i])
				y_points.append(y[i+1])

			switch = 1 - switch

	return p_points, y_points 



def plot_revenue_all(rev1,rev2,rev3, demands):

	width = 0.2
	ind = np.arange(len(demands))

	fig = plt.figure()
	ax = fig.add_subplot(111)
	rects1 = ax.bar(ind, rev1, width, color='y')
	rects2 = ax.bar(ind+width, rev2, width, color='r')
	rects3 = ax.bar(ind+width*2, rev3, width, color='b')

	ax.set_xlabel('Demand Scenarios')
	ax.set_ylabel('Revenue Levels')
	ax.set_title('Bar Plot of Revenues of all Models')

	ax.set_xticks(ind+width)
	ax.set_xticklabels( ('1','2','3','4','5','6','7','8','9','10') )

	ax.legend( (rects1[0], rects2[0], rects3[0]), ('Unconstrained', 'Monotonic', 'Tranche Constrained') )

	plt.show()

	
if __name__ == "__main__":
	main()
