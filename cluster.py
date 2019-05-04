
from gurobipy import *
import offer_stack as offer_stack
import get_data
import string
import constraints
import set_model
import random as random
import csv as csv
from pprint import pprint
from numpy import linspace
import random
import matplotlib.pyplot as plt
import datetime
import numpy
import os
import pickle as pickle
from pprint import pprint
from numpy import linspace
from scipy import linalg
import time
from pulp import *




ZERO = 1e-5
utility_step = 0.01
stage_dep = 1
out_of_sample_pick = 1
def Dispatch(date_folder,sc,dem_levels,range_dict,cluster_dict,date,sample):
    n_d = [sc]
    tp = "TP"+str(sc*1+1)
    price_list = [str(tp)]
    for dem_level in dem_levels:   
        m = Model("dispatch")
        (trans_cap, d, r,d_tranches,d_prices,d_quantities,r_tranches,r_prices,r_quantities,nodes,strategic_nodes,islands,buses, I,beta
           ,arc_id, arc_from, arc_to, arc_cap, fixed_loss, R, X, num_loss_tranches,gen_nodes,dem_nodes,bt1_rhs) = set_model.Set_Param(sc,date_folder)  
        (m,d_x,f,theta,d_y,r_y,r_x) = set_model.Set_LP_Vars(m,gen_nodes,nodes,strategic_nodes,arc_id,buses,trans_cap,d_quantities,r_quantities,d_tranches,r_tranches)
        #d_price = {}
        #r_price = {}
        #d_quantity = {}
        #r_quantity = {}
        #demands = {}
        #reserves = {}
        #nodes = {}
        #gen_nodes = {}
        #dem_nodes = {}
        #d_tranche = {}
        #r_tranche = {}
        #d_offer_data ={}
        #r_offer_data = {}
        #d_M = {}
        #r_M = {}
        #d_y_inc_val= {}
        #d_pi_inc_val= {}
        #r_y_inc_val= {}
        #r_pi_inc_val= {}
        #bt1_rhs={}
        #contracts = {}
        #contract_quantity = {}
        #N      = {}
        #I      = {}
        #beta            = {}
        #buses           = {}
        #arc_id          = {}
        #arc_from        = {}
        #arc_to          ={}
        #arc_cap         ={}
        #R = {}
        #X = {}
        #d_gen_cap                 = {}
        #gen_q                   = {}
        #gen_c                   = {}
        #r_gen_cap                 = {}
        #r_gen_q                   = {}
        #r_gen_c                   = {}     
        #CBT_RHS =0  
        #rho={}

        #m = Model("dispatch")
        #trans_cap = arc_cap
        #d = demands
        #r = reserves
        #d_x={}
        #r_x={}
        #f={}
        #d_p = {}
        #d_y = {}
        #r_p = {}
        #r_y = {}
        #d_tranches={}
        #d_prices={}
        #d_quantities={}
        #r_tranches={}
        #r_prices={}
        #r_quantities={}
        #lambd = {}
        #pi = {}
        #rpi = {}
        #theta = {}
        #dem_cons = {}
        #res_cons = {}    
        #for i in n_d:        
        #    (d_tranches[i], d_prices[i], d_quantities[i]) = offer_stack.SplitDataByNode(
        #        nodes, d_tranche, d_price, d_quantity, d_M )
        #    d_tranches[i]    = dict(zip( nodes, d_tranches[i] ))
        #    d_prices[i]      = dict(zip( nodes, d_prices[i] ))
        #    d_quantities[i]  = dict(zip( nodes, d_quantities[i] ))
        #    for n in nodes:
        #        d_sort_list = zip(d_prices[i][n], d_tranches[i][n],d_quantities[i][n] )
        #        list.sort(d_sort_list)
        #        (d_prices[i][n], d_tranches[i][n],d_quantities[i][n] ) = zip(*d_sort_list)    
                    
        #    d_x[i]={}
        #    f[i]={}
        #    lambd[i] = {}
        #    theta[i] = {}
        #    d_y[i]={}
        #    r_y[i]={}
        #    (r_tranches[i], r_prices[i], r_quantities[i]) = offer_stack.SplitDataByNode(
        #        nodes, r_tranche, r_price, r_quantity, r_M  )
        #    r_tranches[i]    = dict(zip( nodes, r_tranches[i] ))
        #    r_prices[i]      = dict(zip( nodes, r_prices[i] ))
        #    r_quantities[i]  = dict(zip( nodes, r_quantities[i] ))
        #    for n in nodes:
        #        r_sort_list = zip(r_prices[i][n], r_tranches[i][n],r_quantities[i][n] )
        #        list.sort(r_sort_list)
        #        (r_prices[i][n], r_tranches[i][n],r_quantities[i][n] ) = zip(*r_sort_list)
        #    r_x[i]={}              
            #for n in gen_nodes:
            #        d_x[i][n]={}
            #        for t in range(len(d_tranches[i][n])):
            #                d_x[i][n][t] = m.addVar(lb = 0.0, ub = d_quantities[i][n][t]
            #                                        , name = "d_x_%s_%s_%s" % (t,n,i)) 
            #for n in nodes:        
            #        r_x[i][n]={}
            #        for t in range(len(r_tranches[i][n])):
            #                r_x[i][n][t] = m.addVar(lb = 0.0, ub = r_quantities[i][n][t]
            #                                        , name = "r_x_%s_%s_%s" % (t,n,i)) 
            #for n in strategic_nodes:
            #        d_y[i][n] = m.addVar(lb = 0.0, ub = 800 
            #                                ,name = "Strategic_electricity_Offer_%s_%s" % (n,i))
            #        r_y[i][n] = m.addVar(lb = 0.0, ub = 800
            #                                , name = "Strategic_reserve_Offer_%s_%s" % (n,i))
            #for a in arc_id:
            #        f[i][a] = m.addVar(lb = -trans_cap[a], ub = trans_cap[a]
            #                            , name = "f_%s_%s" % (a,i))
            #for b in buses:
            #        theta[i][b] = m.addVar(lb = 0, ub = 10000
            #                                ,name = "PowerAngle_%s_%s" %(i,b))
            #m.update()
        for n in strategic_nodes:
            m.addConstr(d_y[n]==dem_level,name="fixed_consumption")     
            m.addConstr(r_y[n]<=d_y[n],name="energy-reserve")
        m.update()             
        constraints.Generator_Bathtub_Constraint_1(m, d_x , r_x, bt1_rhs
                , gen_nodes, d_tranches, r_tranches,0,0) 
        dem_cons = constraints.d_Meet_Demand(d_tranches,m, d_y, d_x, d
            , beta, f, nodes,gen_nodes
            , strategic_nodes, buses, arc_id, arc_from, arc_to, 0,0)
        res_cons = constraints.r_Meet_Demand(r_tranches, m, r_y, r_x,r
            , beta, nodes, strategic_nodes, buses, 0, islands , I,0)
        m.update()

        constraints.Kirchoff_Loop_Law(m, f, X, theta, arc_id, arc_from, arc_to, 0,0)          
        d_p={}
        r_p={}
        for i in n_d:
            for n in gen_nodes:
                for t in range(len(d_tranches[n])):
                    d_p[n,t]=d_prices[n][t]
        for i in n_d:
            for n in nodes:
                for t in range(len(r_tranches[n])):
                    r_p[n,t]=r_prices[n][t]

        objective = (quicksum(d_p[n,t]*d_x[n][t] 
                      for n in gen_nodes for t in range(len(d_tranches[n]))) 
                        +  quicksum(r_p[n,t]*r_x[n][t] 
                          for n in nodes for t in range(len(r_tranches[n])))  )
        m.setObjective(objective)
        m.update()
        m.optimize()             
        if m.status == GRB.status.OPTIMAL:
                m.write('dispatch.sol')          
                for n in strategic_nodes:
                    for b in buses:
                        if beta[n,b]> 0:   
                            price_value= dem_cons[b].getAttr(GRB.attr.Pi)
                            price_list.append(price_value)
                            price_range= Get_price_range(price_value)
                            range_dict[sc][date]= range_dict[sc][date] + str(price_range)
        if m.status == GRB.Status.INFEASIBLE:
   # Turn presolve off to determine whether model is infeasible
    # or unbounded
            price_list.append("NA")
            range_dict[sc][date]= range_dict[sc][date] + "0"
            m.computeIIS()
            m.write("model.ilp")
            
      

    if range_dict[sc][date] not in cluster_dict[sc].keys():
        cluster_dict[sc][range_dict[sc][date]]= [date]
    else:
        cluster_dict[sc][range_dict[sc][date]].append(date)


    with open('cluster_data_%s.csv' %date, 'ab') as fp0:
                    all = csv.writer(fp0)
                    all.writerow(price_list)

    with open('tp_cluster_dates_%s.csv'%sample, 'ab') as fp1:
                    all1 = csv.writer(fp1)
                    all1.writerow([str(sc),range_dict[sc][date],date])

    return(range_dict,cluster_dict)

def Get_price_range(price):
    range = 0
    if price <= 30:
        range = 1
    elif price <= 60 :
        range = 2 
    else:
        range = 3

    return(range)
def Read_Range_Dict(numberOf_tp,f_range):
    range_dict = {}
    for tp in range(numberOf_tp):
        range_dict[tp]={}
        f1 = csv.reader(open(f_range, 'r'))
        for range_csv in f1:
            if (int(range_csv[0]) == tp):
                range_dict[tp][range_csv[2]] = range_csv[1]

    return(range_dict)         
        


def Cluster(range_dict,numberOf_tp,sample):
    total = {}
    probs_dict = {}
    for t1 in range(-1,numberOf_tp-1):
        t2 = t1+1
        probs_dict[t1]={}
        total[t1] ={}
        if t1 <0:
            range_dict[t1] = {}
            for date in range_dict[t2].keys():
                range_dict[t1][date] = range_dict[t2][date]

        for date in range_dict[t1].keys():
            if t1 < 0 :
                range_dict[t1][date] = 0
            if range_dict[t1][date] not in probs_dict[t1].keys():
                probs_dict[t1][range_dict[t1][date]] = {}
                total[t1][range_dict[t1][date]] = 1
            else:
                total[t1][range_dict[t1][date]] += 1

            if range_dict[t2][date] not in probs_dict[t1][range_dict[t1][date]].keys():

                probs_dict[t1][range_dict[t1][date]][range_dict[t2][date]] = 1
            else:
                probs_dict[t1][range_dict[t1][date]][range_dict[t2][date]] += 1 


    for t1 in range(-1,numberOf_tp-1):
        for c1 in probs_dict[t1].keys():
            for c2 in probs_dict[t1][c1].keys():
                probs_dict[t1][c1][c2]= float(float(probs_dict[t1][c1][c2]) / float(total[t1][c1]))
                for c3 in probs_dict[t1].keys():
                    if c3 != c1:
                        for c4 in probs_dict[t1][c3].keys():
                            if c4 not in probs_dict[t1][c1].keys():
                                probs_dict[t1][c1][c4]=0
           
                      
    with open('rho_%s.csv'%sample, 'ab') as fp2:
        all2 = csv.writer(fp2)
        for t1 in range(-1,numberOf_tp-1):
            for c1 in probs_dict[t1].keys():
                for c2 in probs_dict[t1][c1].keys():
                    all2.writerow([str(t1),c1,c2,str(probs_dict[t1][c1][c2])]) 

    return probs_dict        

def main():
    dates_list = []
    price_dict = {}
    cluster_dict = {}
    (numberOf_tp,dem_levels,sample) =  get_data.Get_Range_Data()
    for root, dirs, files in os.walk("./"+sample):  
        for dirname in dirs:
            dates_list.append(dirname)    
    for sc in range(numberOf_tp):
        price_dict[sc] ={} 
        cluster_dict[sc] = {}
        for date in dates_list:
            price_dict[sc][date] = ""
            (price_dict,cluster_dict)= Dispatch("./"+sample+"/"+date+"/",sc,dem_levels,price_dict,cluster_dict,date,sample)

    #price_dict = Read_Range_Dict(numberOf_tp,'tp_cluster_dates_%s.csv'%sample)
    return (price_dict ,cluster_dict,  Cluster(price_dict,numberOf_tp,sample))
    
     

      
if __name__ == "__main__":
        main()
