
from gurobipy import *
import offer_stack as offer_stack
import get_data
import string
import constraints
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


def Set_Param(sc,date_folder):
        
    tp = "TP"+str(sc+1)
    d_price = {}
    r_price = {}
    d_quantity = {}
    r_quantity = {}
    demands = {}
    reserves = {}
    nodes = {}
    gen_nodes = {}
    dem_nodes = {}
    d_tranche = {}
    r_tranche = {}
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
    N      = {}
    I      = {}
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
    CBT_RHS =0  
    rho={}
    (strategic_nodes, d_gen_cap, gen_q, gen_c,r_gen_cap) = get_data.Strategic_Consumer_Data()        
    (nodes, demands) = get_data.Get_Node_Data(tp, date_folder + "TradePeriodNode.csv"
                                    , date_folder + "TradePeriodNodeDemand.csv")
    (islands,reserves)= get_data.Get_Reserve_Data(tp, date_folder + "TradePeriodIslandReserve.csv")
    bt1_rhs = get_data.Get_BT1_RHS_Data(tp,  date_folder + "TradePeriodBT1RHS1.csv")
    (buses, I)   = get_data.Get_Bus_Data(tp, date_folder + "TradePeriodBusIsland.csv")
    (beta) = get_data.Get_Bus_Allocation_Factor(tp, nodes, buses, date_folder
                + "TradePeriodNodeBusAllocationFactor.csv")
    (arc_id, arc_from, arc_to, arc_cap, 
            fixed_loss, R, X, num_loss_tranches) = get_data.Get_Arc_Data(tp,  date_folder 
                + "TradePeriodBranchDefn.csv", 
                date_folder + "TradePeriodBranchOpenStatus.csv",
                date_folder + "TradePeriodBranchCapacity.csv",
                date_folder + "TradePeriodBranchParameter.csv")
    gen_nodes = get_data.Get_Gen_Nodes(tp , date_folder + "TradePeriodEnergyOffer.csv" )
    dem_nodes= get_data.Get_Dem_Nodes(tp , date_folder + "TradePeriodNodeDemand.csv" )
    (d_offer_data)= get_data.Get_Energy_Offer_Data(tp, date_folder 
            + "TradePeriodEnergyOffer.csv", strategic_nodes)
    d_tranche= d_offer_data.keys()
    (d_price, d_quantity, d_M) = splitDict(d_offer_data)
    (r_offer_data)= get_data.Get_Reserve_Offer_Data(tp, date_folder 
                + "TradePeriodSustainedILROffer.csv", date_folder
                + "TradePeriodSustainedPLSROffer.csv", date_folder 
                    + "TradePeriodSustainedTWDROffer.csv",strategic_nodes)
    r_tranche = r_offer_data.keys()
    (r_price, r_quantity, r_M)= splitDict(r_offer_data)
    (contracts, contract_quantity, N) = get_data.Contract_Data(nodes
                    , buses, beta, I, demands)
        
    trans_cap = arc_cap
    d = demands
    r = reserves
    d_tranches={}
    d_prices={}
    d_quantities={}
    r_tranches={}
    r_prices={}
    r_quantities={}   
           
    (d_tranches , d_prices , d_quantities ) = offer_stack.SplitDataByNode(
        nodes, d_tranche, d_price, d_quantity, d_M )
    d_tranches     = dict(zip( nodes, d_tranches  ))
    d_prices       = dict(zip( nodes, d_prices  ))
    d_quantities   = dict(zip( nodes, d_quantities  ))
    for n in nodes:
        d_sort_list = zip(d_prices[n], d_tranches[n],d_quantities[n] )
        list.sort(d_sort_list)
        (d_prices[n], d_tranches[n],d_quantities[n] ) = zip(*d_sort_list)  
    (r_tranches, r_prices, r_quantities) = offer_stack.SplitDataByNode(
        nodes, r_tranche, r_price, r_quantity, r_M  )
    r_tranches    = dict(zip( nodes, r_tranches ))
    r_prices      = dict(zip( nodes, r_prices ))
    r_quantities  = dict(zip( nodes, r_quantities ))
    for n in nodes:
        r_sort_list = zip(r_prices[n], r_tranches[n],r_quantities[n] )
        list.sort(r_sort_list)
        (r_prices[n], r_tranches[n],r_quantities[n] ) = zip(*r_sort_list)  

    return(trans_cap, d, r,d_tranches,d_prices,d_quantities,r_tranches,r_prices,r_quantities,nodes,strategic_nodes,islands,buses, I,beta
           ,arc_id, arc_from, arc_to, arc_cap, fixed_loss, R, X, num_loss_tranches,gen_nodes,dem_nodes,bt1_rhs )

def Set_LP_Vars(m,gen_nodes,nodes,strategic_nodes,arc_id,buses,trans_cap,d_quantities,r_quantities,d_tranches,r_tranches):

   
    d_x={}
    f={}
    theta= {}
    d_y={}
    r_y={}
    r_x={}  
                
    for n in gen_nodes:
            d_x[n]={}
            for t in range(len(d_tranches[n])):
                    d_x[n][t] = m.addVar(lb = 0.0, ub = d_quantities[n][t]
                                            , name = "d_x_%s_%s" % (t,n)) 
    for n in nodes:        
            r_x[n]={}
            for t in range(len(r_tranches[n])):
                    r_x[n][t] = m.addVar(lb = 0.0, ub = r_quantities[n][t]
                                            , name = "r_x_%s_%s" % (t,n)) 
    for n in strategic_nodes:
            d_y[n] = m.addVar(lb = 0.0, ub = 800 
                                    ,name = "Strategic_electricity_Offer_%s" % (n))
            r_y[n] = m.addVar(lb = 0.0, ub = 800
                                    , name = "Strategic_reserve_Offer_%s" % (n))
    for a in arc_id:
            f[a] = m.addVar(lb = -trans_cap[a], ub = trans_cap[a]
                                , name = "f_%s" % (a))
    for b in buses:
            theta[b] = m.addVar(lb = 0, ub = 10000
                                    ,name = "PowerAngle_%s" %(b))
    m.update()

    return(m,d_x,f,theta,d_y,r_y,r_x)



def Set_MIP_Vars(m,gen_nodes,nodes,d_tranches,r_tranches,arc_id,trans_cap,d_x,r_x,buses,islands):

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
        #Flow variable
        f = {}
        # Flow constraint duals
        eta1 = {}
        eta2 = {}
        #Flow big M binaries
        z_eta1 = {}
        z_eta2 = {}
        lambd = {}
        pi = {}
        theta = {}
        X = {}
        #Total generation and reserve of each generator
        total_d_x = {}
        total_r_x = {}
        #Getting generation stacks data
        for n in gen_nodes:
            bt_dual1[n] = m.addVar(lb = 0.0,ub = 10000.0, name = "bt_dual1_%s" % (n))
            ug[n] = {}
            for t in range(len(d_tranches[n])):
                ug[n][t] = m.addVar(lb = 0.0,ub = 10000.0, name = "ug_%s_%s" % (t,n)) 
        for n in nodes:
                rug[n] = {}
                for t in range(len(r_tranches[n])):
                    rug[n][t] = m.addVar(lb = 0.0,ub = 10000.0, name = "rug_%s_%s" % (t,n))
        m.update()
        for n in nodes:
                        
                d_p[n] = m.addVar(lb = -2000.0,ub = 20000.0,name = "d_p(t)_%s" %(n))
        for l in islands:  
                r_p[l] = m.addVar(lb = -2000.0,ub = 20000.0,name = "r_p(t)_%s" %(l))
        m.update()
    
 
                
        for a in arc_id:
                eta1[a]              = m.addVar(lb = 0, ub = 10000, name = "Electricity_Flow_Capacity_Dual_%s" % (a) )
                eta2[a]              = m.addVar(lb = 0, ub = 10000, name = "Electricity_Reverse_Flow_Capacity_Dual%s" % (a) )
                lambd[a]             = m.addVar(lb = - 10000000, ub = 10000000, name = "Electricity_Lambda_%s" %(a))
        m.update()
       
        for n in gen_nodes:
            total_d_x[n] = m.addVar(lb = 0.0,ub = 10000000,name ="total_d_x_%s" %(n))
            m.update()
            m.addConstr( total_d_x[n] == sum(d_x[n][t] for t in range(len(d_tranches[n])) ), "Cons_total_d_x_%s" %(n))
                    
        for n in nodes:
            total_r_x[n] = m.addVar(lb = 0.0,ub = 10000000,name ="total_r_x_%s" %(n))
            m.update()
            m.addConstr( total_r_x[n] == sum(r_x[n][t] for t in range(len(r_tranches[n])) ), "Cons_total_r_x_%s" %(n))
        m.update()     

        for b in buses:
                pi[b]        = m.addVar(lb = 0.0, ub = 10000,name ="BusPrice_%s" %(b))
        m.update()

        return(d_p,r_p,bt_dual1,gen_costs,ug,rug,eta1,eta2,z_eta1 , z_eta2,lambd,pi , total_d_x ,total_r_x)