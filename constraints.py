
from gurobipy import *
import offer_stack as offer_stack
import random as random
import csv as csv
from pprint import pprint
from numpy import linspace
import random
import matplotlib.pyplot as plt
import datetime
import numpy

ZERO = 1e-5


     
def Generator_Capacity(m, d_y, r_y, d_gen_cap, r_gen_cap, strategic_nodes, scen_no,j):
        '''
        Generation at strategic nodes less than the strategic generation capacity.
        '''
        for n in strategic_nodes:
          m.addConstr(d_y[n] <= d_gen_cap[n] 
         , "Generation Capacity %s_%s" %(n,scen_no))

def Consumer_utility():
    u = utility
    return u

def Generator_Costs(m, d_y, gen_costs, strategic_nodes, d_gen_cap, gen_c, gen_q, scen_no,j):
        '''
        Applies a linear piecewise approximation of generation costs according to the
        points specified in gen_c and gen_q, the costs and quantities, respectively.
        '''
        gc_alpha = {}
        for i in strategic_nodes:
                gc_set          = sorted(range(len(gen_q[i])))               
                for j in gc_set:
                        gc_alpha[i,j]  = m.addVar(0.0, 1.0, name = "gc_alpha_%s_%s" %(i,scen_no))
                m.update()
                m.addConstr(gen_costs[i]  == quicksum(gc_alpha[i,j] * round(gen_c[i][j])
                                       for j in gc_set ), "Generation_Costs_%s" %i)
                m.addConstr(d_y[i] == quicksum(gc_alpha[i,j] * round(gen_q[i][j]) 
                                               for j in gc_set ), "Match_Cost_Quantity_%s" %i)
                m.addConstr(quicksum(gc_alpha[i,j] for j in gc_set) == 1 , "Sum_alpha(gc)_%s" %i)
                m.addSOS(GRB.SOS_TYPE2, [gc_alpha[i,j]  for j in gc_set])

def d_Meet_Demand(d_tranches, m, d_y, d_x, d, beta, f, nodes,gen_nodes
                  , strategic_nodes, buses, arc_id, arc_from, arc_to, scen_no,j):
        '''
        Meet nodal demands, as well as conservation of flow at each bus.
        '''
        d_cons = {}
        for b in buses:
                d_cons[b] = m.addConstr(quicksum( -beta[n,b]*d_y[n]    for n in strategic_nodes)
                ==  quicksum( beta[n,b]*d[n]  for n in nodes)
                -   quicksum(beta[n,b]*d_x[n][t]  for n in gen_nodes 
                    for t in range(len(d_tranches[n])))
                +  quicksum( f[a] for a in arc_id if arc_from[a]  == b)
                -   quicksum(       f[a] 
                        for a in arc_id if arc_to[a]    == b)
                , "d_Meet_Demand_%s_%s" % (b, scen_no))
        return(d_cons)

def d_Meet_Demand_Losses(m, d_y, d_q, d, beta, f, nodes
                         , strategic_nodes, buses, arc_id, arc_from, arc_to, line_loss, scen_no):
        '''
        Meet nodal demands, as well as conservation of flow at each bus. Includes losses.
        '''
        for b in buses:
                m.addConstr(quicksum(  -beta[n,b]*d_y[n]  for n in strategic_nodes)
                        ==  quicksum( beta[n,b]*d[n]  for n in nodes)
                        -  quicksum( beta[n,b]*d_q[n]  for n in nodes)
                        +  quicksum( f[a]  for a in arc_id if arc_from[a]  == b)
                        - quicksum(f[a]    for a in arc_id if arc_to[a]    == b)
                        +  0.5*quicksum(   line_loss[a]  for a in arc_id if arc_from[a]  == b)
                        + 0.5*quicksum(   line_loss[a]  for a in arc_id if arc_to[a]    == b)
                        ,  "d_Meet_Demand_%s_%s" % (b, scen_no))

def r_Meet_Demand(r_tranches, m, r_y, r_x, r, beta,  nodes
          , strategic_nodes, buses, scen_no ,islands,  I,j):
        '''
        Meet nodal demands, as well as conservation of flow at each bus.
        '''
        r_cons = {}
        for l in islands:           
            r_cons[l] = m.addConstr(sum(   r_y[n] for n in strategic_nodes if Find_Island(buses, beta, n , I)==l)
                    - r[l] +  sum(r_x[n][t]  for n in nodes  if Find_Island(buses, beta, n ,I)==l 
                         for t in range(len(r_tranches[n]))),GRB.EQUAL,0
                    , "r_Meet_Demand_%s_%s" % (l, scen_no))
        return(r_cons)

def Piecewise_Line_Losses(m, f, line_loss, phi, arc_id
            , trans_cap, price, R, fixed_loss, arc_has_losses
            , num_loss_tranches, f_alpha):
        '''
        Applies a piecewise linear approximation for losses. 
        The losses are derived from a series of convex cuts 
        but are implemented as a piecewise linear function.
        The condition of convexity is important for the dual
        variable phi to remain correct in the formulation.

        This is why Line_Loss_Calculations needs to be
        called twice - once to set up the piecewise points, and
        then again to ensure the values refer to the
        convex implementation for the a, b, and phi's.
        '''
        (ll_pieces, ll_points, f_values, ll_values, ll_a, ll_b) = Line_Loss_Calculations_Piecewise(
            arc_id, R, fixed_loss, trans_cap, arc_has_losses, num_loss_tranches)
        for a in arc_id:
                for k in ll_points[a]:
                        f_alpha[a,k] = m.addVar(0.0,1.0,name = "alpha(f)")
                m.update()
                m.addConstr(    line_loss[a]  ==  quicksum( ll_values[a,k] * f_alpha[a,k]   for k in ll_points[a] )
                            , "Piecewise_Loss_%s" % a)
                m.addConstr(    f[a]      ==      quicksum(       f_values[a,k] * f_alpha[a,k]  
                                                     for k in ll_points[a] ), "Piecewise_Loss_%s" % a)
                m.addConstr(    quicksum(f_alpha[a,k]   for k in ll_points[a]) == 1, "Sum_alpha(f)_%s" % a)
                m.addSOS(GRB.SOS_TYPE2, [f_alpha[a,k]   for k in ll_points[a]])
                # Complimentary Slackness
                for k in ll_pieces[a]:
                    m.addConstr(phi[a,k] <= 5000*(f_alpha[a,2*k] + f_alpha[a,2*k+1])
                    , "Phi_Orthogonality_%s_%s" % (a,k))
                m.addSOS(GRB.SOS_TYPE2, [phi[a,k] for k in ll_pieces[a]])
        (ll_pieces, ll_points, f_values, ll_values, ll_a, ll_b) = Line_Loss_Calculations_Convex(
            arc_id, R, fixed_loss, trans_cap, arc_has_losses, num_loss_tranches)
        return (ll_a, ll_b)

def Line_Loss_Calculations_Piecewise(arc_id, R, fixed_loss, trans_cap, arc_loss, num_tranches=0):
        '''
        Sets up the flow points and loss points for piecewise line losses.
        '''
        loss_gradients  = {}    
        loss_intercepts = {}
        loss_values     = {}
        flow_values     = {}
        pieces = {}
        points = {}
        for a in arc_id:
                # Set up flow points - doubled up for each interior point
                if arc_loss[a]:
                        flow_points = []
                        flow_points.append(-trans_cap[a])
                        for k in range(2*num_tranches[a]-1):
                                flow_points.append(flow_points[-1] 
                                + trans_cap[a]/num_tranches[a])
                                flow_points.append(flow_points[-1])
                        flow_points.append(trans_cap[a])
                else:
                        flow_points = [-trans_cap[a], 0.0, 0.0, trans_cap[a]]
# In the piecewise implementation, n flow points implied n/2 flow pieces.
                points[a] = range(len(flow_points))
                pieces[a] = range(len(flow_points)/2)   
 # Set up loss points corresponding to the flow points
                if arc_loss[a]:
                        (ll_val, ll_a, ll_b) = Line_Loss_Function(
                        flow_points, R[a], fixed_loss[a])
                else:
                        ll_val = [0.0]*len(flow_points)
                        ll_a   = [0.0]*(len(flow_points)/2)

                for k in points[a]:
                        flow_values[a,k] = flow_points[k]
                        loss_values[a,k] = ll_val[k]

                for k in pieces[a]:
                        loss_gradients[a,k]  = ll_a[k]
                        loss_intercepts[a,k] = ll_b[k]
        return (pieces, points, flow_values, loss_values, loss_gradients, loss_intercepts)

def Line_Loss_Calculations_Convex(arc_id, R, fixed_loss, trans_cap, arc_loss, num_tranches=0):
        '''
        Sets up the flow points and loss points for convex line losses.
        '''
        loss_gradients  = {}    
        loss_intercepts = {}
        loss_values     = {}
        flow_values     = {}
        pieces = {}
        points = {}
        for a in arc_id:
                # Set up flow points
                if arc_loss[a]:
                        flow_points = []
                        flow_points.extend(  linspace(-trans_cap[a], 0.0, num_tranches[a]+1)  )
                        flow_points.pop(-1)
                        flow_points.extend(  linspace(0.0, trans_cap[a], num_tranches[a]+1)  )
                else:
                        flow_points = [-trans_cap[a], 0.0, trans_cap[a]]

                # In the convex implementation, n flow points implied n-1 flow pieces.
                points[a] = range(len(flow_points))
                pieces[a] = range(len(flow_points)-1)   
                # Set up loss points corresponding to the flow points
                if arc_loss[a]:
                        (ll_val, ll_a, ll_b) = Line_Loss_Function(flow_points, R[a], fixed_loss[a])
                else:
                        ll_val = [0.0]*len(flow_points)
                        ll_a   = [0.0]*(len(flow_points)-1)
                for k in points[a]:
                        flow_values[a,k] = flow_points[k]
                        loss_values[a,k] = ll_val[k]
                for k in pieces[a]:
                        loss_gradients[a,k]  = ll_a[k]
                        loss_intercepts[a,k] = ll_b[k]                        
        return (pieces, points, flow_values, loss_values, loss_gradients, loss_intercepts)

def Line_Loss_Function(flow, R, C):
	'''
	Generates a set of points, l, corresponding to the losses
	for each quantity, and calculates the gradients and
	intercepts for lines between each l.
	INPUTS:     flow            - a list of flow points
		      R                       - resistance on a line
		      C                       - fixed loss on a line
	RETURNS:    l           - a list of line loss values
	      a           - a list of gradients for each piece
	      b           - a list of intercepts for each piece
	'''
	l = []
	a = []
	b = []	    
	for f in flow:
		l.append( R * f * f + C)
	for i in range(len(flow)-1):
	# Check if two adjacent flows are equal
		if (abs(flow[i+1] - flow[i]) < ZERO):
			a.append( 0.0  )
			b.append( l[i] )
		else:
			a.append(  (l[i+1] - l[i])/(flow[i+1] - flow[i])  )
		b.append(  l[i] - a[i]*flow[i]  )
	return (l,a,b)

def Costumer_Bathtub_Constraint(m,d_y , r_y , CBT_RHS , strategic_nodes,scen_no,j):
    for n in strategic_nodes:
        m.addConstr( d_y[n] - r_y[n] >= CBT_RHS, name = "Consumer_Bathtub_%s_%s_%s" % (n,scen_no,j))
        m.update()
def Generator_Bathtub_Constraint_1(m,d_x , r_x , bt1_rhs, gen_nodes, d_tranches, r_tranches, i,j) :
    for n in gen_nodes: 
        m.addConstr((sum(d_x[n][t] for t in range(len(d_tranches[n])) ) + sum( r_x[n][t] 
                for t in range(len(r_tranches[n])))- bt1_rhs[n]) ,GRB.LESS_EQUAL,0 , "Bathtub_%s_%s" %(n,i))
   
def Arc_Stationarity(m, pi, eta1, eta2, lambd, X, arc_id, arc_from, arc_to, scen_no,j):
        '''
        First order KKT condition for arc flows.
        '''
        for a in arc_id:
                m.addConstr(-pi[arc_from[a]] + pi[arc_to[a]] - eta1[a] + eta2[a] + lambd[a] * X[a] == 0,
                            "Arc_Stationarity_%s_%s_%s" %(a,scen_no,j))

def d_Price_Stationarity(m, gen_nodes , d_tranches, d_prices, d_p , ug , bt_dual1,i ,j):
        '''
        First order KKT condition for arc gen tranches.
        '''
        for n in gen_nodes:
            for t in range(len(d_tranches[n])):
                m.addConstr(d_prices[n][t] - d_p[n] + ug[n][t] + bt_dual1[n], GRB.GREATER_EQUAL , 0,
                            "d_Price_Stationarity_%s_%s_%s_%s" %(n,t,i,j))

def r_Price_Stationarity(m, nodes ,gen_nodes, r_tranches
                         , r_prices, r_p , rug , bt_dual1, islands, buses , beta ,I,scen_no,j):
        '''
        First order KKT condition for arc res tranches.
        '''
        for l in islands:
            for n in nodes:
                 for t in range(len(r_tranches[n])):
                    if Find_Island(buses, beta, n , I)==l :
                        if n in gen_nodes:
                            m.addConstr(r_prices[n][t] - r_p[l] + rug[n][t] + bt_dual1[n], GRB.GREATER_EQUAL , 0,
                                        "r_Price_Stationarity_%s_%s_%s_%s" %(n,t, scen_no,j))
                        else:
                            m.addConstr(r_prices[n][t] - r_p[l] + rug[n][t] , GRB.GREATER_EQUAL , 0,
                                        "r_Price_Stationarity_%s_%s_%s_%s" %(n,t,scen_no,j))

def Arc_Stationarity_Losses(m, pi, eta1, eta2, lambd, X, arc_id, arc_from, arc_to, phi, ll_a, ll_pieces, scen_no,j):
        '''
        First order KKT condition for arc flows including convex losses.
        '''
        #print ll_a.keys()
        for a in arc_id:
                m.addConstr(-pi[arc_from[a]] + pi[arc_to[a]] - eta1[a] + eta2[a] + lambd[a] * X[a] 
                                -               quicksum(  ll_a[a,k]*phi[a,k]  for k in ll_pieces[a])
                                ==              0, "Arc_Stationarity_%s_%s" %(a,j))

def Loss_Stationarity(m, pi, phi, arc_id, arc_from, arc_to, ll_pieces, scen_no):
        '''
First order KKT condition for the convex line losses.
        '''
        for a in arc_id:
                m.addConstr(0.5*(pi[arc_from[a]] + pi[arc_to[a]])
                        ==    quicksum(  phi[a,k] for k in ll_pieces[a]), "Loss_Stationarity_%s" %a)

def Kirchoff_Loop_Law(m, f, X, theta, arc_id, arc_from, arc_to, scen_no,j):
        '''
Kirchoff's loop law giving relations between arc flows and bus power angles. Alternative to the
sum of voltage differences in a loop = 0.
        '''
        for a in arc_id:
                if not((a=="BEN_HAY1.1") or (a=="BEN_HAY2.1") or (a=="HAY_BEN1.1") or (a=="HAY_BEN2.1")):
                        m.addConstr( X[a] * f[a]
                        == theta[arc_from[a]]
                        -  theta[arc_to[a]], "Kirchoff's_Law_%s_%s_%s" %(a,scen_no,j))

def Power_Angle_Stationarity(m, lambd, buses, arc_id, arc_from, arc_to,j, scen_no):
        '''
First order KKT condition for the power angles at buses.
        '''
        for b in buses:
            m.addConstr(quicksum(lambd[a]  for a in arc_id if (arc_to[a]==b)
                         and not( (arc_from[a]=="580" and b=="420") 
                         or (arc_from[a]=="420" and b=="580")))
                        -    quicksum(lambd[a]       for a in arc_id
                           if (arc_from[a]==b) and not( (arc_to[a]=="580" 
                          and b=="420")   or (arc_to[a]=="420"   and b=="580")))
                        ==   0.0, "Power_Angle_Stationarity_%s_%s_%s" %(b,scen_no,j))

                
def Flow_Complementary_Slackness(m, price, eta1, eta2, trans_cap, f, arc_id,j, scen_no):
        '''
        Complementary slackness conditions on arc flows at capacity or at reverse capacity.
        '''
        # Flow Constraints Complimentary Slackness
        z_eta1 = {}
        z_eta2 = {}
        for a in arc_id:
                z_eta1[a] = m.addVar(vtype = GRB.BINARY, name = "Eta1Master_%s_%s_%s" %(a,scen_no,j))
                z_eta2[a] = m.addVar(vtype = GRB.BINARY, name = "Eta2Master_%s_%s_%s" %(a,scen_no,j))
        m.update()

        for a in arc_id:
                m.addConstr(eta1[a]  <= 5000* z_eta1[a], 
                                "Flow_Capacity1.%s_%s_%s" %(a,scen_no,j))
                m.addConstr(trans_cap[scen_no][a] - f[a] <= ( 2*trans_cap[scen_no][a] ) * (1-z_eta1[a]),
                                "Flow_Capacity2.%s_%s_%s" %(a,scen_no,j))
                m.addConstr(eta2[a]  <= 5000* z_eta2[a],
                                "Reverse_Flow_Capacity1.%s_%s_%s" %(a,scen_no,j))
                m.addConstr(trans_cap[scen_no][a] + f[a] <= ( 2*trans_cap[scen_no][a] ) * (1-z_eta2[a]),
                                "Reverse_Flow_Capacity2.%s_%s_%s" %(a,scen_no,j))
                m.addConstr(z_eta1[a] + z_eta2[a] <= 1)
        return (z_eta1,z_eta2)
def BT_Complementary_Slackness(m, d_x,r_x, bt_dual1, bt1_rhs
                    , scen_no, gen_nodes, d_tranches , r_tranches,j):
    z_bt1 = {}
    for n in gen_nodes:           
        z_bt1[n] = m.addVar(vtype = GRB.BINARY, name = "BinaryBTDual_%s_%s_%s" %(n,scen_no,j))            
    m.update()
    for n in gen_nodes: 
        m.addConstr((bt1_rhs[n] - (sum(d_x[n][t] for t in range(len(d_tranches[n])) )+ sum( r_x[n][t] 
        for t in range(len(r_tranches[n]))) )- 6000*z_bt1[n]),GRB.LESS_EQUAL,0
                    , name = "Comp1_BinaryBTDual_%s_%s_%s" %(n,scen_no,j))
        m.addConstr((bt_dual1[n]- 6000*(1- z_bt1[n])),GRB.LESS_EQUAL,0
                    , name = "Comp2_BinaryBTDual_%s_%s_%s" %(n,scen_no,j))        
    m.update()

def d_Tranche_Complementary_Slackness(m, d_x,d_quantities
                    ,d_prices, d_p , ug , bt_dual1, scen_no, gen_nodes, d_tranches,j):
    d_z1_tranche= {}
    d_z2_tranche= {}
    for n in gen_nodes:
        d_z1_tranche[n]={}
        d_z2_tranche[n]={}
        for t in range(len(d_tranches[n])):
            d_z1_tranche[n][t] = m.addVar(vtype = GRB.BINARY
                    , name = "d_BinaryTrancheComplementarity1_%s_%s_%s_%s" %(n,t,scen_no,j))
            d_z2_tranche[n][t] = m.addVar(vtype = GRB.BINARY
              , name = "d_BinaryTrancheComplementarity2_%s_%s_%s_%s" %(n,t,scen_no,j))              
    m.update()
    for n in gen_nodes:
        for t in range(len(d_tranches[n])):  
           m.addConstr(d_quantities[n][t] - d_x[n][t] -
             d_quantities[n][t]*(1-d_z1_tranche[n][t]) ,GRB.LESS_EQUAL,0, 
               "Tranche_Comp_Slack_1.%s.%s_%s_%s" %(n,t,scen_no,j))
           m.addConstr(ug[n][t]- 6000*d_z1_tranche[n][t] ,GRB.LESS_EQUAL,0, 
                  "Tranche_Comp_Slack_2.%s.%s_%s_%s" %(n,t,scen_no,j))
           m.addConstr( d_x[n][t] - d_quantities[n][t]*(1-d_z2_tranche[n][t]) ,GRB.LESS_EQUAL,0, 
              "Tranche_Comp_Slack_3.%s.%s_%s_%s" %(n,t,scen_no,j))
           m.addConstr((d_prices[n][t] - d_p[n] + ug[n][t] + bt_dual1[n]
                - 6000*d_z2_tranche[n][t] ),GRB.LESS_EQUAL,0, 
              "Tranche_Comp_Slack_4.%s.%s_%s_%s" %(n,t,scen_no,j))
    m.update()
    return( d_z1_tranche,d_z2_tranche)

def d_improve_Big_M( m, scen_no, gen_nodes, d_tranches, d_z1_tranche, d_z2_tranche,j):
    for n in gen_nodes:
        for t in range(len(d_tranches[n])):
            if t!= len(d_tranches[n])-1  :
                m.addConstr(d_z1_tranche[n][t]-d_z1_tranche[n][t+1] ,GRB.GREATER_EQUAL,0, 
                                    "d_Improve_Big_M_1.%s.%s_%s_%s" %(n,t,scen_no,j))
                m.addConstr(d_z2_tranche[n][t]-d_z2_tranche[n][t+1] ,GRB.LESS_EQUAL,0, 
                                    "d_Improve_Big_M_2.%s.%s_%s_%s" %(n,t,scen_no,j))
        m.addConstr(sum(d_z1_tranche[n][t]+ d_z2_tranche[n][t] for t in range(len(d_tranches[n])) )
                    ,GRB.LESS_EQUAL,len(d_tranches[n]), 
                            "d_Improve_Big_M_3.%s.%s" %(n,scen_no))
        m.addConstr(sum(d_z1_tranche[n][t]+ d_z2_tranche[n][t] for t in range(len(d_tranches[n])) ) 
                    ,GRB.GREATER_EQUAL, len(d_tranches[n])-1,
                            "d_Improve_Big_M_4.%s.%s" %(n,scen_no))
    m.update()

def r_Tranche_Complementary_Slackness(m, r_x,r_quantities,r_prices, r_p 
      , rug , bt_dual1, scen_no, nodes, gen_nodes,r_tranches, islands, buses, beta , I,j):
    r_z1_tranche= {}
    r_z2_tranche= {}
    for n in nodes:
        r_z1_tranche[n]={}
        r_z2_tranche[n]={}
        for t in range(len(r_tranches[n])):
            r_z1_tranche[n][t] = m.addVar(vtype = GRB.BINARY
                 , name = "r_BinaryTrancheComplementarity1_%s_%s_%s_%s" %(n,t,scen_no,j))
            r_z2_tranche[n][t] = m.addVar(vtype = GRB.BINARY
                 , name = "r_BinaryTrancheComplementarity2_%s_%s_%s_%s" %(n,t,scen_no,j))           
    m.update()
    for n in nodes:
        for t in range(len(r_tranches[n])):  
           m.addConstr(r_quantities[n][t] - r_x[n][t] 
                       - r_quantities[n][t]*(1- r_z1_tranche[n][t]) ,GRB.LESS_EQUAL,0, 
                          "r_Tranche_Comp_Slack_1.%s.%s_%s_%s" %(n,t,scen_no,j))
           m.addConstr((rug[n][t]- 6000*r_z1_tranche[n][t] ),GRB.LESS_EQUAL,0, 
                                "r_Tranche_Comp_Slack_2.%s.%s_%s_%s" %(n,t,scen_no,j))
           m.addConstr( r_x[n][t] - r_quantities[n][t]*(1-r_z2_tranche[n][t]) ,GRB.LESS_EQUAL,0, 
                               "r_Tranche_Comp_Slack_3.%s.%s_%s_%s" %(n,t,scen_no,j))
           for l in islands:
               if Find_Island(buses, beta, n , I)==l :
                   if n in gen_nodes:
                        m.addConstr((r_prices[n][t] - r_p[l] + rug[n][t] + bt_dual1[n]
                                     - 6000*r_z2_tranche[n][t] ),GRB.LESS_EQUAL,0, 
                                        "r_Tranche_Comp_Slack_4.%s.%s_%s_%s" %(n,t,scen_no,j))
                   else:
                        m.addConstr((r_prices[n][t] - r_p[l] + rug[n][t] 
                                     - 6000*r_z2_tranche[n][t] ),GRB.LESS_EQUAL,0, 
                                        "r_Tranche_Comp_Slack_4.%s.%s_%s_%s" %(n,t,scen_no,j))
    m.update()
    return( r_z1_tranche,r_z2_tranche)
def r_improve_Big_M( m, scen_no, nodes,r_tranches, r_z1_tranche, r_z2_tranche,j):
    for n in nodes:
        for t in range(len(r_tranches[n])):
            if t!= len(r_tranches[n])-1  :
                m.addConstr(r_z1_tranche[n][t]-r_z1_tranche[n][t+1] ,GRB.GREATER_EQUAL,0, 
                                    "r_Improve_Big_M_1.%s.%s_%s_%s" %(n,t,scen_no,j))
                m.addConstr(r_z2_tranche[n][t]-r_z2_tranche[n][t+1] ,GRB.LESS_EQUAL,0, 
                                    "r_Improve_Big_M_2.%s.%s_%s_%s" %(n,t,scen_no,j))
        m.addConstr(sum(r_z1_tranche[n][t]+ r_z2_tranche[n][t] for t in range(len(r_tranches[n])) ) 
                    ,GRB.LESS_EQUAL,len(r_tranches[n]), 
                            "r_Improve_Big_M_3.%s.%s" %(n,scen_no))
        m.addConstr(sum(r_z1_tranche[n][t]+ r_z2_tranche[n][t] for t in range(len(r_tranches[n])) ) 
                    ,GRB.GREATER_EQUAL, len(r_tranches[n])-1,
                            "r_Improve_Big_M_4.%s.%s" %(n,scen_no))
    m.update()
def d_IP_Constraints(m, strategic_nodes, d_y, d_p, n_d,scen,j):
        '''
        Integer programming constraints to ensure that marginal 
        price and residual demand points are monotonic
        '''
        # Enumeration Constraints
        d_z = {}
        for n in strategic_nodes:
                d_z[n] = {}
                for i in n_d:
                    for j in n_d:               
                        if i != j:
                            d_z[n][i,j] = m.addVar(vtype = GRB.BINARY
                                , name = "d_IP_Z_Var_%s_%s_%s_%s" % (n,i,j,scen))
        m.update()
        for n in strategic_nodes:
                for i in n_d:
                    for j in n_d:
                        if j != i:
                                m.addConstr(d_y[i][n] <= d_y[j][n]  + 8000*d_z[n][i,j]
                                    , name = "d_IP_Constraints1_%s_%s_%s_%s" %(n,i,j,scen))
                                m.addConstr(d_p[j][n] <= d_p[i][n] + 5000*d_z[n][i,j]
                                     , name = "d_IP_Constraints2_%s_%s_%s_%s" %(n,i,j,scen))             
                for i in n_d:
                    for j in n_d:
                        if j > i:
                            m.addConstr(d_z[n][i,j] + d_z[n][j,i] == 1, 
                                name = "d_IP_Constraints3_%s_%s_%s_%s" %(n,i,j,scen))
def r_IP_Constraints(m, strategic_nodes, r_y, r_p, n_d,islands, buses, beta,I,scen,j):
        '''
        Integer programming constraints to ensure that marginal
        price and residual demand points are monotonic
        '''
        # Enumeration Constraints
        r_z = {}
        for n in strategic_nodes:
                r_z[n] = {}
                for i in n_d:
                    for j in n_d:               
                        if i != j:
                            r_z[n][i,j] = m.addVar(vtype = GRB.BINARY
                            , name = "r_IP_Z_Var_%s_%s_%s_%s" %(n,i,j,scen))
        m.update()
        for n in strategic_nodes:
            for l in islands:
                if Find_Island(buses[0], beta[0], n , I[0])==l:
                    for i in n_d:
                        for j in n_d:
                            if j != i:
                                m.addConstr(r_y[i][n] <= r_y[j][n]  + 8000*r_z[n][i,j]
                                            , name = "r_IP_Constraints1_%s_%s_%s_%s"% (n,i,j,scen))
                                m.addConstr(r_p[i][l] <= r_p[j][l] + 5000*r_z[n][i,j]
                                            , name = "r_IP_Constraints2_%s_%s_%s_%s"% (n,i,j,scen))            
            for i in n_d:
                for j in n_d:
                    if j > i:
                        m.addConstr(r_z[n][i,j] + r_z[n][j,i] == 1
                                    , name = "r_IP_Constraints3_%s_%s_%s_%s" %(n,i,j,scen))

def Tranche_Constraints(m, nodes, d_y, p, tranche_no, n_d):
        '''
        Tranche constraints formulated as an assignment 
        problem to to limit the number of tranches
        '''
        Qa={}
        Pa={}
        gammaP={}
        gammaQ={}
        for n in nodes:
                Qa[n] = {}
                Pa[n] = {}                
                gammaP[n] = {}
                gammaQ[n] = {}
                Qa[n][0] = 0
                Pa[n][0] = 0
                Pa[n][num_tranches+1]=2000
                for i in range(0,num_tranches+1):
                    Qa[n][i]=m.addVar(name='Residual_Demand_Level_%s_%s' % (n,i))
                    Pa[n][i]=m.addVar(name='Marginal_Price_Level_%s_%s' % (n,i))
                    gammaP[n][i]={}
                    gammaQ[n][i]={}
                    for j in n_d:
                        if(i!=0): 
                            gammaP[n][i][j]=m.addVar(vtype=GRB.BINARY
                            ,name='gammaP'+str(i)+'_'+str(j))
                        gammaQ[n][i][j]=m.addVar(vtype=GRB.BINARY,name='gammaQ'+str(i)+'_'+str(j))
                Pa[n][num_tranches+2]=m.addVar(vtype=GRB.BINARY,name='Pa'+str(i))
        m.update()
        # Tranche Constraints
        for n in nodes:
            for j in n_d:
                m.addConstr(quicksum(gammaP[n][i][j] for i in range(1,num_tranches+1)) 
                 + quicksum(gammaQ[n][i][j] for i in range(0,num_tranches+1)) == 1)
                temp=[]
                for i in range(0,num_tranches+1):
                    temp.append(gammaQ[n][i][j])
                for i in range(1,num_tranches+1):
                    temp.append(gammaP[n][i][j])
                m.addSOS(GRB.SOS_TYPE1, temp)
                for i in range(0,num_tranches+1):
                    for j in n_d:
                        m.addConstr(p[j][n]>=Pa[n][i]-1000*(1-gammaQ[n][i][j]))
                        m.addConstr(p[j][n]<=Pa[n][i+1]+1000*(1-gammaQ[n][i][j]))
                        m.addConstr(y[j][n]>=Qa[n][i]-1000*(1-gammaQ[n][i][j]))
                        m.addConstr(y[j][n]<=Qa[n][i]+1000*(1-gammaQ[n][i][j]))                            
                for i in range(1,num_tranches+1):
                    for j in n_d:
                        m.addConstr(p[j][n]>=Pa[n][i]-1000*(1-gammaP[n][i][j]))
                        m.addConstr(p[j][n]<=Pa[n][i]+1000*(1-gammaP[n][i][j]))
                        m.addConstr(y[j][n]>=Qa[n][i-1]-1000*(1-gammaP[n][i][j]))
                        m.addConstr(y[j][n]<=Qa[n][i]+1000*(1-gammaP[n][i][j]))
                for i in range(1,num_tranches):
                    m.addConstr(Pa[n][i]<=Pa[n][i+1]);
                    m.addConstr(Qa[n][i]<=Qa[n][i+1]);
                m.addConstr(Qa[n][0] == 0)
def Find_Node(nodes, beta, b):
        '''
        Returns the node name of a bus
        '''
        for n in nodes:
                if beta[n,b] > 0.0:
                        return n

def Find_Island(buses, beta, n, I):
        '''
        Returns the island of a node
        '''
        for b in buses:
            if beta[n,b] > 0.0:      
                return I[b]
                break

def main():
    
    print "Getting constraints"

if __name__ == "__main__":
        main()
