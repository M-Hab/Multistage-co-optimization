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
max_u = 100
u_step = 1
ZERO = 1e-5

def S_MIP(tp,c,folders,last_u_c,u_list,u_d_dict,u_p_dict,write_dict,utility,last_y, last_p,sample,mip_gap = 0.001,fixed_cons='NA') :


    m = Model("OMEN")
    d_price = {}
    r_price = {}          
    d_quantity = {}
    r_quantity = {}
    demands = {}
    d = {}
    reserves = {}
    r = {}
    nodes = {}
    nodes_null = {}
    gen_nodes = {}
    dem_nodes = {}
    d_tranches = {}
    r_tranches = {}
    d_offer_data ={}
    r_offer_data = {}
    d_M = {}
    r_M = {}
    d_y_inc_val= {}
    d_pi_inc_val= {}
    r_y_inc_val= {}
    r_pi_inc_val= {}
    bt1_rhs={}
    contracts = {}
    contract_quantity = {}
    N                               = {}
    I                               = {}
    beta            = {}
    buses           = {}
    arc_id          = {}
    arc_from        = {}
    arc_to          ={}
    arc_cap         ={}
    R = {}
    X = {}
    d_gen_cap                 = {}
    gen_q                   = {}
    gen_c                   = {}
    r_gen_cap                 = {}
    r_gen_q                   = {}
    r_gen_c                   = {}
    d_x={}
    r_x={}
    d_tranches={}
    d_prices={}
    d_quantities={}
    r_tranches={}
    r_prices={}
    r_quantities={}
    trans_cap = {}
    f = {}
    #Electricity price
    d_p = {}
    #Strategic consumer consumption
    d_y = {}
    #Reserve price
    r_p = {}
    #Strategic consumer reserve offer
    r_y = {}
    #Bathtub constraint dual 
    bt_dual1 = {}
    #generation costs
    gen_costs = {}
    # Bathtub constraint dual variables
    ug = {}
    rug = {}
    # Flow constraint duals
    eta1 = {}
    eta2 = {}
    #Flow big M binaries
    z_eta1 = {}
    z_eta2 = {}
    lambd = {}
    #Loss variables
    line_loss = {}
    phi = {}
    num_loss_tranches = {}
    #Bus price
    pi = {}
    theta = {} 
    X = {}
    #Total generation and reserve of each generator
    total_d_x = {}
    total_r_x = {}
    #Tranche big M binary variables
    d_z1_tranche ={}
    d_z2_tranche = {}
    r_z1_tranche ={}
    r_z2_tranche = {}
    fixed_loss = {}
    active_line_losses = 0
    CBT_RHS = 0
    ip_on=0
    tranche_on=0
    losses_on=0
    active_utility = 0
    #Getting generation stacks data     
    for i in range(len(folders)):
        (trans_cap[i], d[i], r[i],d_tranches[i],d_prices[i],d_quantities[i],r_tranches[i],r_prices[i],r_quantities[i],nodes[i],strategic_nodes,islands,buses[i], I[i],beta[i]
           ,arc_id[i], arc_from[i], arc_to[i], arc_cap[i], fixed_loss[i], R[i], X[i], num_loss_tranches[i],gen_nodes[i],dem_nodes[i],bt1_rhs[i]) = set_model.Set_Param(tp,folders[i])  
        (m,d_x[i],f[i],theta[i],d_y[i],r_y[i],r_x[i]) = set_model.Set_LP_Vars(m,gen_nodes[i],nodes[i],strategic_nodes,arc_id[i],buses[i],trans_cap[i],d_quantities[i],r_quantities[i],d_tranches[i],r_tranches[i])
        (d_p[i],r_p[i],bt_dual1[i],gen_costs[i],ug[i],rug[i],eta1[i],eta2[i],z_eta1[i] , z_eta2[i],lambd[i],pi[i] , total_d_x[i] ,total_r_x[i])=set_model.Set_MIP_Vars(m,gen_nodes[i]
            ,nodes[i],d_tranches[i],r_tranches[i],arc_id[i],trans_cap[i],d_x[i],r_x[i],buses[i],islands)     

        #Bathtub constraints
        constraints.Costumer_Bathtub_Constraint(m, d_y[i] , r_y[i] , CBT_RHS , strategic_nodes, i,0)
        constraints.Generator_Bathtub_Constraint_1(m, d_x[i] , r_x[i], bt1_rhs[i] , gen_nodes[i], d_tranches[i], r_tranches[i],i,0) 
        if active_utility:
            u = constraints.Consumer_utility()
        # Line losses
        if active_line_losses:                  
                # Determine from num_loss_tranches if an arc has losses applied or not
                arc_has_losses = {}
                for a in arc_id[i]:
                        if (num_loss_tranches[a]==0):
                                arc_has_losses[a] = 0
                        else:
                                arc_has_losses[a] = 1

                (ll_pieces, ll_points, f_values, ll_values, ll_a, ll_b) = constraints.Line_Loss_Calculations_Piecewise(arc_id[i], R[i], fixed_loss, trans_cap[i], arc_has_losses, num_loss_tranches)
                f_alpha[i]={}                        
                (ll_a, ll_b) = constraints.Piecewise_Line_Losses(m, f[i], line_loss[i], phi[i], arc_id[i], trans_cap[i], price[i], R[i], fixed_loss, arc_has_losses, num_loss_tranches, f_alpha[i])

        constraints.d_Meet_Demand(d_tranches[i],m, d_y[i], d_x[i], d[i], beta[i], f[i], nodes[i],gen_nodes[i], strategic_nodes, buses[i], arc_id[i], arc_from[i], arc_to[i], i,0)
        constraints.r_Meet_Demand(r_tranches[i], m, r_y[i], r_x[i],r[i], beta[i], nodes[i], strategic_nodes, buses[i], i, islands , I[i],0)
        for n in nodes[i]:
            m.addConstr(d_p[i][n]  == quicksum(beta[i][n,b]*pi[i][b] for b in buses[i] ), "Node_Bus_Price_Relation_%s_Demand_%s_%s" % (n,i,0))
            m.update()
        # Kirchoff's loop flow laws
        constraints.Kirchoff_Loop_Law(m, f[i], X[i], theta[i], arc_id[i], arc_from[i], arc_to[i], i,0)
        # Stationarity conditions for dual
        if active_line_losses:
                constraints.Arc_Stationarity_Losses(m, pi[i], eta1[i], eta2[i], lambd[i], X[i], arc_id[i], arc_from[i], arc_to[i], phi[i], ll_a, ll_pieces, i)
                constraints.Loss_Stationarity(m, pi[i], phi[i], arc_id[i], arc_from[i], arc_to[i], ll_pieces, i)
                constraints.Power_Angle_Stationarity(m, lambd[i], buses[i], arc_id[i], arc_from[i], arc_to[i],0, i)
        else:
                constraints.Arc_Stationarity(m, pi[i], eta1[i], eta2[i], lambd[i], X[i], arc_id[i], arc_from[i], arc_to[i], i,0)
                constraints.Power_Angle_Stationarity(m, lambd[i], buses[i], arc_id[i], arc_from[i], arc_to[i], 0,i)
        #BathTub constraints complemantary slackness conditions
        constraints.BT_Complementary_Slackness(m, d_x[i],r_x[i], bt_dual1[i], bt1_rhs[i], i, gen_nodes[i], d_tranches[i], r_tranches[i],0)
        # Arc flow complementary slackness conditions
        (z_eta1[i], z_eta2[i]) = constraints.Flow_Complementary_Slackness(m, d_prices[i], eta1[i], eta2[i], trans_cap, f[i], arc_id[i], 0,i)
        # Tranche complementary slackness conditions
        constraints.d_Price_Stationarity(m, gen_nodes[i] , d_tranches[i], d_prices[i], d_p[i] , ug[i] , bt_dual1[i],i ,0 )
        constraints.r_Price_Stationarity(m, nodes[i] ,gen_nodes[i], r_tranches[i], r_prices[i], r_p[i] , rug[i] , bt_dual1[i],islands, buses[i],beta[i] ,I[i],i,0)
        ( d_z1_tranche[i],d_z2_tranche[i])= constraints.d_Tranche_Complementary_Slackness(m, d_x[i],d_quantities[i],d_prices[i], d_p[i] , ug[i] , bt_dual1[i], i, gen_nodes[i], d_tranches[i],0)
        #constraints.d_improve_Big_M( m,i, gen_nodes[i], d_tranches[i], d_z1_tranche[i], d_z2_tranche[i],0)
        ( r_z1_tranche[i],r_z2_tranche[i])= constraints.r_Tranche_Complementary_Slackness(m, r_x[i],r_quantities[i],r_prices[i], r_p[i] , rug[i] , bt_dual1[i], i, nodes[i],gen_nodes[i], r_tranches[i], islands, buses[i], beta[i] , I[i],0)
        #constraints.r_improve_Big_M( m, i, nodes[i],r_tranches[i], r_z1_tranche[i], r_z2_tranche[i],0)
        m.update()
    # Integer programming constraints - Monotonicity constraints
        if ip_on:
            constraints.d_IP_Constraints(m, strategic_nodes, d_y[i], d_p[i], scen_d,i,0)
            constraints.r_IP_Constraints(m, strategic_nodes, r_y[i], r_p[i] , scen_d, islands, buses[i],beta[i], I[i],i,0)
        # Tranches constraints
        if tranche_on:
                constraints.d_Tranche_Constraints(m, nodes, d_y, d_p, n_d, tranche_no)
                constraints.r_Tranche_Constraints(m, nodes, r_y, r_p, n_d, tranche_no)
    # zero allocated demand for strategic consumer
        for n in strategic_nodes:
            d[i][n] = 0

    for n in strategic_nodes:
        for i in range(len(folders)):
            for j in range(len(folders)):
                if i != j :
                    m.addConstr((d_y[i][n]==d_y[j][n] ), "StochasticMIP_demand_%s_%s_%s" % (n,i,j))
                    m.addConstr((r_y[i][n]==r_y[j][n] ), "StochasticMIP_res_%s_%s_%s" % (n,i,j))
    if fixed_cons !='NA':
        for n in strategic_nodes:
            for i in range(len(folders)):
                    m.addConstr((d_y[i][n] == fixed_cons ), "Fixed_strategic_demand_%s_%s" % (n,i))               
        
    if losses_on:
            objective = (   quicksum( rho[i] * (
                                    quicksum( pq[i][n] - d[i][n]*p[i][n] + r_pq[i][n]           for n in nodes[i]  )
                                        - r[i]['NI']*(bt_dual1[i]['WKM2201 MOK0']+ r_p[i]['WKM2201 MOK0'])        
                                    - r[i]['SI']*(bt_dual1[i]['COL0661 COL0']+ r_p[i]['COL0661 COL0']) 
                                    + quicksum( bt_dual1[i][n]*bt1_rhs[i][n]                          for n in gen_nodes[i])
                                    + quicksum( trans_cap[i][a]*(eta1[i][a] + eta2[i][a])             for a in arc_id[i] )
                                    + quicksum( gen_costs[i][s]                                       for s in strategic_nodes if gen_costs_on)
                                    - quicksum( Consumer_utility()* d_y[i][s]                           for s in strategic_nodes if utility_on)
                                    - quicksum( ll_b[a,k] * phi[i][a,k]                               for a in arc_id[i] for k in ll_pieces[a] if losses_on  )
                                    + quicksum( p[i][n]*contract_quantity[i][c]                       for n in nodes[i] for c in contracts[i] if N[i][c]==n and gen_contracts)
                                                                            ) for i in n_d) )
    else:            
        objective = (   quicksum( 1 * (
                                    quicksum(  - d[i][n]*d_p[i][n]          for n in nodes[i]  )
                                    + quicksum(  - r[i][l]*(r_p[i][l])          for l in islands  )     
                                    + quicksum( bt_dual1[i][n]*bt1_rhs[i][n]                          for n in gen_nodes[i])                           
                                    + quicksum( trans_cap[i][a]*(eta1[i][a] + eta2[i][a])             for a in arc_id[i] )
                                    + quicksum( ug[i][n][t]*d_quantities[i][n][t]                                       for n in gen_nodes[i]  for t in range(len(d_tranches[i][n])))
                                    + quicksum( rug[i][n][t]*r_quantities[i][n][t]                                       for n in nodes[i]  for t in range(len(r_tranches[i][n])))
                                    + quicksum( d_prices[i][n][t]*d_x[i][n][t]                                       for n in gen_nodes[i]  for t in range(len(d_tranches[i][n]))) 
                                    + quicksum( r_prices[i][n][t]*r_x[i][n][t]                                       for n in nodes[i]  for t in range(len(r_tranches[i][n]))) 
                                    - utility* (sum(   d_y[i][n]                    for n in strategic_nodes))
                                                                            ) for i in range(len(folders)) ) )
    m.setObjective(objective)
    m.setParam('MIPGap', mip_gap)
    m.setParam('TimeLimit', 10000)
    m.update()
    #m.write("temp2.lp")
    m.optimize()             
    if m.status == GRB.status.OPTIMAL or (m.status == GRB.status.TIME_LIMIT and m.MIPGap <= 2): 
        if sample == "outofsample":  
            with open('simulation_y.csv', 'ab') as fp0:
                all0 = csv.writer(fp0)
                for s_n in strategic_nodes:
                    all0.writerow([str(utility),str(tp),str(c),str(d_y[0][s_n].getAttr('x') ),str(d_p[0][s_n].getAttr('x') ),str(r_y[0][s_n].getAttr('x') ),str(r_p[0]['SI'].getAttr('x') )])
            return(d_y[0][s_n].getAttr('x'),d_p[0][s_n].getAttr('x'),r_y[0][s_n].getAttr('x'),r_p[0]['SI'].getAttr('x'))

        else:         
            with open('all_utility.csv', 'ab') as fp0:
                all0 = csv.writer(fp0)
                for s_n in strategic_nodes:
                    all0.writerow([str(utility),str(tp),str(c),str(d_y[0][s_n].getAttr('x') )])

            y_temp = round(d_y[0][s_n].getAttr('x'),1)  
            p_temp =  d_p[0][s_n].getAttr('x')      
            u_d_dict[utility]=y_temp
            u_p_dict[utility]=p_temp
        
    if m.status == GRB.status.INFEASIBLE or (m.status == GRB.status.TIME_LIMIT and m.MIPGap > 2):
        if sample == "outofsample":
            return("NA","NA","NA","NA")

        else:
            u_d_dict[utility]= last_y
            u_p_dict[utility]= last_p
            y_temp=last_y
            p_temp= last_p
            
            stop_it = 1
            with open('all_utility.csv', 'ab') as fp0:
                all0 = csv.writer(fp0)
                all0.writerow([utility,str(tp),str(c),"NA"])



    if sample != "outofsample":
        fix = 0    
        not_last = 0
        write_u_list= []
        stop_it = 0
        next_ut = -2 
        u_d_dict[-2] = -0.1
        first_u = 0   

        prev_remove_some_u=[] 
        while u_d_dict[next_ut] >= -0.1 and first_u == 0:
            remove_some_u=[] 
            remove_list=[] 
            if next_ut != -2 :
                utility = next_ut 
            with open('bisection_uc_data.csv', 'ab') as fp01:
                all01 = csv.writer(fp01)
                
                this_ut_consumption =str(y_temp)                                
                #If utility is zero
                if utility == 0:
                    write_dict[utility] = [u_d_dict[utility],u_p_dict[utility]]
                    #all01.writerow([str(utility),str(i),str(scen_k),str(round(d_y[i][j][r].getAttr('x'),3)),str(d_p[i][j][r].getAttr('x'))])
                    u_d_dict[max_u] = -1
                    u_list.append(max_u)
                    first_u = 1
                #If utility is nonzero
                else:
                    if len(u_list) == 0:
                        if utility == max_u-1:
                            if max_u  not in write_dict.keys():
                                for x in write_dict:
                                    write_u_list.append(x)
                                write_u_list.sort()
                                for x in write_u_list:
                                    all01.writerow([str(x),str(tp),str(c),str(write_dict[x][0]),str(write_dict[x][1])])
                                all01.writerow([str(max_u),str(tp),str(c),str(800),str(u_p_dict[max_u])])
                                break
                    if utility == max_u and u_d_dict[utility] == 0:
                        all01.writerow([str(0),str(tp),str(c),str(0),str(0)])
                        all01.writerow([str(utility),str(tp),str(c),u_d_dict[utility],u_p_dict[utility]])
                        break
                    for u in u_list:                           
                        if u != utility:
                            if u_d_dict[u] != -1 :
                                if len(remove_some_u) !=0:
                                    if u < our_u:
                                        continue
                                    if u == our_u:
                                        utility = our_u
                                        continue
                                    if u > our_u:
                                        utility = our_u
                                        if ((u - utility) > u_step) or ((u - utility) < -u_step) :
                                            for u_w in remove_some_u:                                                                                                                               
                                                u_list.remove(u_w)
                                                del u_d_dict[u_w]
                                        else:
                                            prev_remove_some_u=remove_some_u
                                            remove_some_u = []
                                if u_d_dict[u] != u_d_dict[utility]:
                                    if ((u - utility) > u_step) or ((u - utility) < -u_step) :
                                        if utility == max_u:
                                            u_d_dict[utility] = 800
                                        u_d_dict[(u+utility)/2] = -1
                                        next_ut = (u+utility)/2
                                        u_list.append((u+utility)/2) 
                                                        
                                        break
                                    else:
                                        if u<utility:
                                            write_dict[utility] = [u_d_dict[utility],u_p_dict[utility]]
                                        else:
                                            write_dict[u] = [u_d_dict[u],u_p_dict[u]]
                                        if u_d_dict[utility] < 799.4 :

                                            #all01.writerow([str(utility),str(i),str(scen_k),str(round(d_y[i][j][r].getAttr('x'),3)),str(d_p[i][j][r].getAttr('x'))])
                                            #all01.writerow([str(u),str(i),str(scen_k),str(u_d_dict[u])])

                                            #if u_list[(1+ u_list.index(utility))] == utility:
                                            #    u_list.remove(u_list[(1+ u_list.index(utility))])
                                            #    del u_d_dict[u_list[(1+ u_list.index(utility))]]

                                            remove_list = []
                                            if u<utility:
                                                for w in u_list:
                                                                
                                                    if w > utility:
                                

                                                        if u_d_dict[w] > u_d_dict[utility]:
                                                            if ((w - utility) > u_step) or ((w - utility) < -u_step):
                                                                if w != max_u:
                                                                    if len(remove_list) > 0 :

                                                                        if u_d_dict[w] < u_d_dict[u_list[1+ u_list.index(w)]]:

                                                                    # u_d_dict[w] = -1

                                                                            next_ut = w
                                                                            not_last = 1
                                                                            break
                                                                        else:
                                                                            remove_list.append(w)
                                                                    else:

                                                                        next_ut = w
                                                                        not_last = 1
                                                                        break
                                                                else:
                                                                    next_ut = w
                                                                    not_last = 1
                                                            else:
                                                                remove_list.append(w)

                                                if next_ut != -2:
                                                                
                                                    for w in u_list:
                                                        if w > utility and w < u_list[u_list.index(next_ut)-1] : 
                                                                if u_d_dict[w] == u_d_dict[utility]:
                                                                    remove_list.append(w)

                                                if len(remove_list)>0:
                                                    for r_w in remove_list:
                                                        u_list.remove(r_w)
                                                        del u_d_dict[r_w]                                                                                                                             
                                                u_list.remove(u)
                                                del u_d_dict[u]

                                            else:

                                                for w in u_list:                                                                
                                                    if w > u:
                                                        if u_d_dict[w] > u_d_dict[u]:
                                                            next_ut = w
                                                            not_last = 1
                                                            break
                                                if next_ut != -2:
                                                    to_remove=[]
                                                    for w in u_list:
                                                        if w > u and w < next_ut : 
                                                                if u_d_dict[w] == u_d_dict[u]:
                                                                    to_remove.append(u)
                                                                    u = w
                                                    for u in to_remove:

                                                        u_list.remove(u)
                                                        del u_d_dict[u]
                                                                                       
                                                        #if w > u and w < u_list[u_list.index(next_ut)-1] : 
                                                        #        if u_d_dict[w] == u_d_dict[u]:
                                                        #            u_list.remove(u)
                                                        #            del u_d_dict[u]
                                                        #            u = w
                                                if next_ut == -2:
                                                    if u_d_dict[u] >799.4:
                                                        u_d_dict[next_ut] = -0.5
                                                        for x in write_dict:
                                                            write_u_list.append(x)
                                                        write_u_list.sort()
                                                        for x in write_u_list:
                                                            all01.writerow([str(x),str(tp),str(c),str(write_dict[x][0]),str(write_dict[x][1])])
                                                                
#                                                                next_ut = u_list[(1+ u_list.index(u))]
                                                # u_d_dict[u_list[(1+ u_list.index(u))]]= -1
                                            #u_d_dict[u]= -1
                                            if next_ut != -2:
                                                if u_list[u_list.index(next_ut) - 1] != utility:

                                                    u_list.remove(utility)
                                                    del u_d_dict[utility]
                                            else:
                                                u_list.remove(utility)
                                                del u_d_dict[utility]
                                            if len(prev_remove_some_u) != 0:
                                                for u_w in prev_remove_some_u:
                                                    if  u_w in  u_list:                                                                                                                           
                                                        u_list.remove(u_w)


                                                    del u_d_dict[u_w]

                                            break
                                        else:
                                            u_d_dict[next_ut] = -0.5
                                            stop_it =1
                                            for x in write_dict:
                                                write_u_list.append(x)
                                            write_u_list.sort()
                                            for x in write_u_list:
                                                all01.writerow([str(x),str(tp),str(c),str(write_dict[x][0]),str(write_dict[x][1])])
                                            break
                                                                

                                else:
                                                        
                                    #if u< utility:
                                        #remove_some_u.append(u)
                                        for w in u_list:
                                            if   u_d_dict[w] ==u_d_dict[u]:
                                                remove_some_u.append(w)
                                        remove_some_u.sort()
                                        our_u = remove_some_u.pop()


                                    #    break
                                    #else:
                                    #    remove_some_u.append(utility)
                                    #    for w in u_list:
                                    #        if w>u and  u_d_dict[w] ==u_d_dict[u]:
                                    #            remove_some_u.append(w)

                                    #    u_list.remove(utility)
                                    #    del u_d_dict[utility]
                                    #    utility = u


                                       
            u_list = list(set(u_list))
            u_list.sort()

                        
        return (this_ut_consumption,u_list,u_d_dict,u_p_dict,write_dict,stop_it,y_temp,p_temp)           

def  Get_cluster_data(numberOf_tp , f_clusters):
    cluster_dates_dict = {}    
    for tp in range(numberOf_tp):
        f1 = csv.reader(open(f_clusters, 'r'))    
        cluster_dates_dict[tp]= {}
        for cluster_csv in f1:
            if (int(cluster_csv[0]) == tp):
                if cluster_csv[1] not in cluster_dates_dict[tp].keys():
                    cluster_dates_dict[tp][cluster_csv[1]]= [cluster_csv[2]]
                else:
                    cluster_dates_dict[tp][cluster_csv[1]].append(cluster_csv[2])      
    return cluster_dates_dict

def main():
        
    cluster_dates_dict = {}
    (numberOf_tp,dem_levels,sample) =  get_data.Get_Range_Data()
    #cluster_dates_dict = Get_cluster_data(numberOf_tp,'tp_cluster_dates_data.csv')    
    cluster_dates_dict = Get_cluster_data(numberOf_tp,'tp_cluster_dates_%s.csv'%sample)
    for tp in range(4):
        for c in cluster_dates_dict[tp].keys():  
            folders = []    
            for date in cluster_dates_dict[tp][c]:
                folders.append("./"+sample+"/"+date+"/")            
            last_u_c = {}
            last_u_c[-1]= 0  
            u_p_dict={}
            write_dict={}
            last_u = -1
            u_d_dict={}
            u_list = [0]     
            u_d_dict[0] =-1
            last_y=0
            last_p=0
            u_left = 1  
            while u_left==1:
                u_left = 0
                for u in u_list:
                    if u_d_dict[u] ==-1:
                        this_u = u

                (last_u_c[this_u],u_list,u_d_dict,u_p_dict,write_dict,stop_it ,this_y, this_p) = S_MIP(tp,c,folders,last_u_c[last_u],u_list,u_d_dict,u_p_dict,write_dict,this_u,last_y, last_p,sample,mip_gap = 0.001,fixed_cons='NA')
                last_y = this_y
                last_p =  this_p
                for u in u_list:
                    if u_d_dict[u] ==-1:
                        u_left = 1
                        break
                if stop_it == 1:
                    break

if __name__ == "__main__":
        main()
