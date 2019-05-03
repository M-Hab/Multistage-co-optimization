
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



def Get_BT1_RHS_Data(tp , f_bt1rhs):
    f1 = csv.reader(open(f_bt1rhs, 'r'))
    f1.next()
    f1.next()
    bt1_rhs = {}
    for bt1rhs_csv in f1:                          
        if (bt1rhs_csv[0] == tp):                   
            bt1_rhs[bt1rhs_csv[1]] = float(bt1rhs_csv[2])
    return bt1_rhs 
   
def Get_Reserve_Data(tp, f_reserve ):   
        f1 = csv.reader(open(f_reserve, 'r'))
        # Headers
        f1.next()      
        islands = ["NI", "SI"]
        reserves = []    
        reserves = {}
        for i in islands:
                reserves[i] = 0.0
        for reserve_csv in f1:                            
            if (reserve_csv[1] == tp):                   
                reserves[reserve_csv[2]] = float(reserve_csv[4])*1.05
        return ( islands, reserves )

def Get_Node_Data(tp, f_node, f_demand ):
        '''
        Returns node data from vSPD data for a particular trading period.
        INPUTS:
                tp                              - Relevant trading period
                f_node                  - File name for "TradePeriodNode" data
                f_demand                - File name for "TradePeriodNodeDemand" data
        OUTPUTS:
                nodes                   - List of nodes
                demands                 - Dict of demands {NODES}
        '''
        f1 = csv.reader(open(f_node, 'r'))
        f2 = csv.reader(open(f_demand, 'r'))
        # Headers
        f1.next()
        f1.next()
        f2.next()
        f2.next()
        nodes = []
        demands = []        
        for node_csv in f1:
                # Check trading period
                if (node_csv[0] == tp):
                        nodes.append(node_csv[1])      
        demands = {}
        for n in nodes:
                demands[n] = 0.0
        for demand_csv in f2:                          
            if (demand_csv[0] == tp):
                if  float(demand_csv[2])> 0 :
                    demands[demand_csv[1]] = float(demand_csv[2])
                else:
                    demands[demand_csv[1]] = float(demand_csv[2])
                if demand_csv[1] == "TWI2201" :
                    demands[demand_csv[1]] = 0.0
        return (nodes, demands )

def Get_Gen_Nodes(tp , f_gen_node):
     
     f1 = csv.reader(open(f_gen_node, 'r'))
     
     f1.next()
     f1.next()
   
     gen_nodes = []
     
     dem_nodes = []
     
     for gen_node_csv in f1:
            # Check trading period
            if (gen_node_csv[0] == tp):
                if (gen_node_csv[2] == "t1" ):
                    if(gen_node_csv[3] == "i_GenerationMWOffer"):
                        gen_nodes.append(gen_node_csv[1] )
     return gen_nodes



def Get_Dem_Nodes(tp , f_dem_node):
    f1 = csv.reader(open(f_dem_node, 'r'))         
    f1.next()
    f1.next()  
    dem_nodes = []
    for dem_node_csv in f1:
            # Check trading period
            if (dem_node_csv[0] == tp):
                dem_nodes.append(dem_node_csv[1] )
    return dem_nodes

def Get_Bus_Data(tp, f_busisland):
        '''
        Returns bus data from vSPD for a particular trading period.
        INPUTS:
                tp                                              - Relevant trading period
                f_busisland                     - File name for "TradePeriodBusIsland" data
        OUTPUTS:
                buses                                   - List of buses
                I             - Dictionary mapping each bus to "NI" or "SI", North or South Island.
        '''
        f1 = csv.reader(open(f_busisland, 'r'))
        # Headers
        f1.next()
        f1.next()
        buses = []
        I1 = []           
        # Get list of buses
        for csv_bus in f1:
                if (csv_bus[0] == tp):
                        buses.append(csv_bus[1])
                        I1.append(csv_bus[2])
        I= {}
        I = dict(zip(buses,I1))
        return (buses, I)

def Get_Bus_Allocation_Factor(tp, nodes, buses, f_nodebusallocation):
        '''
        Constructs the beta matrix describing which buses appear at which nodes,
        as well as the respective allocation factors.
        INPUTS:
                tp                                              - Relevant trading period
                nodes                                   - List of nodes
                buses                                   - List of buses
                f_nodebusallocation     - File name for "TradePeriodNodeBusAllocationFactor" data
        OUTPUTS:
                beta                                    - node-bus allocation factor dictionary.
        '''

        f1 = csv.reader(open(f_nodebusallocation, 'r'))
        # Headers
        f1.next()
        f1.next()
        # Initialise beta to be all zeros, so all key values are present
        beta    = {}
        for n in nodes:
                for b in buses:
                        beta[n,b] = 0
        # Populate beta using vSPD data
        for csv_busallocation in f1:
                if (csv_busallocation[0] == tp):
                        beta[csv_busallocation[1], csv_busallocation[2]] = float(csv_busallocation[3])
        return (beta)

def Get_Arc_Data(tp, f_branchdefn, f_branchstatus, f_branchcapacity, f_branchparam):
        '''
        Returns arc data from vSPD data for a particular trading period.
        INPUTS:
                tp                                      - Relevant trading period
                f_branchdefn            - File name for "TradePeriodBranchDefn" data
                f_branchstatus          - File name for "TradePeriodBranchOpenStatus" data
                f_branchcapacity        - File name for "TradePeriodBranchCapacity" data
                f_branchparam           - File name for "TradePeriodBranchParam" data
        OUTPUTS:
                arc_id                          - List of arc identifiers (names)
                arc_from                        - Dict of arc heads {ARC_ID}
                arc_to                          - Dict of arc tails {ARC_ID}
                arc_cap                         - Dict of arc capacities {ARC_ID}
                fixed_loss                      - Fixed loss on each arc {ARC_ID}
                R                                       - Resistance on each arc {ARC_ID}
                X                                       - Reactance on each arc {ARC_ID}
                num_tranches            - Number of loss tranches on each arc {ARC_ID}
        '''
        f1 = csv.reader(open(f_branchdefn, 'r'))
        f2 = csv.reader(open(f_branchstatus, 'r'))
        f3 = csv.reader(open(f_branchcapacity, 'r'))
        f4 = csv.reader(open(f_branchparam, 'r'))
        # Headers
        f1.next()
        f1.next()
        f2.next()
        f2.next()
        f3.next()
        f3.next()
        f4.next()
        f4.next()
        arc_id                  = []
        arc_from                = []
        arc_to                  = []
        arc_cap                 = []
        X                               = []
        fixed_loss              = []
        R                               = []
        num_tranches    = []
        for csv_branchdefn in f1:
                status_csv              = f2.next()
                capacities_csv  = f3.next()
                # Check open status
                if (csv_branchdefn[0] == tp) & (status_csv[2] == "0"):
                        # Arcs
                        arc_id.append( csv_branchdefn[1] )
                        arc_from.append( csv_branchdefn[2] )
                        arc_to.append( csv_branchdefn[3] )
                        #lognormal infeasibilty issue
                        arc_cap.append( float(capacities_csv[2])*1.05 )
                        # Fixed losses
                        param_csv = f4.next()
                        fixed_loss.append( 0.0 * float(param_csv[3]) )
                        # Resistance
                        param_csv = f4.next()
                        R.append( 0.1 * float(param_csv[3]) )
                        # Reactance
                        param_csv = f4.next()
                        if (abs(float(param_csv[3])) < ZERO):
                                X.append( 0.0 )
                        else:
                                X.append( 1.0 / float(param_csv[3]) )
                        # num loss tranches
                        param_csv = f4.next()
                        #num_tranches.append( int(param_csv[3]) )
                        num_tranches.append( 0 )
                else:
                        param_csv = f4.next()
                        param_csv = f4.next()
                        param_csv = f4.next()
                        param_csv = f4.next()
        arc_from        = dict(zip(arc_id, arc_from))
        arc_to          = dict(zip(arc_id, arc_to))
        arc_cap         = dict(zip(arc_id, arc_cap))
        fixed_loss  = dict(zip(arc_id, fixed_loss))
        R  = dict(zip(arc_id, R))
        X                       = dict(zip(arc_id, X))
        num_tranches  = dict(zip(arc_id, num_tranches))
        return (arc_id, arc_from, arc_to, arc_cap, fixed_loss, R, X, num_tranches)

def Get_Energy_Offer_Data(tp, f_energyoffer, strategic_nodes):
        '''
        Returns offer data from vSPD for a particular trading period.
        INPUTS:
                tp        - Relevant trading period
                f_energyoffer   - File name for "TradePeriodEnergyOffer" data
                strategic_nodes - A list of strategic node names - offers at these nodes will be skipped.
        OUTPUTS:
                offer_data     - A dictionary indexed by {TRANCHES} containing a tuple of 
                        (price, quantity, tranch_node) for each tranch.
        '''
        f = csv.reader(open(f_energyoffer, 'r'))
        f.next()
        f.next()
        d_tranches                = []
        d_prices                  = []
        d_quantities              = []
        d_tranch_nodes    = []
        for csv_offer in f:
                if (csv_offer[0] == tp):
                        # Ignore offers on strategic nodes
                        if not(csv_offer[1] in strategic_nodes):
                                d_tranches.append(csv_offer[0]+" "+csv_offer[1]+" "+csv_offer[2])
                                d_quantities.append( float(csv_offer[4]) )
                                csv_offer = f.next()
                                d_prices.append( float(csv_offer[4]) )
                                d_tranch_nodes.append(csv_offer[1])
        return dict(zip( d_tranches, zip(d_prices, d_quantities, d_tranch_nodes) ))

def Get_Reserve_Offer_Data(tp,f_sustainedILRoffer,f_sustainedPLSRoffer,f_sustainedTWDRoffer, strategic_nodes):
        '''
        Returns reserve offer data from vSPD for a particular trading period.
        INPUTS:
                tp                              - Relevant trading period
                f_reserveoffer   - File name for "TradePeriodReserveOffer" data
                strategic_nodes - A list of strategic node names - offers at these nodes will be skipped.
        OUTPUTS:
                reserve _offer_data - A dictionary indexed by {TRANCHES} containing a tuple of 
                       (price, quantity, tranch_node) for each tranch.
        '''
        sum_reserve = 0
        f1 = csv.reader(open(f_sustainedILRoffer, 'r'))
        f1.next()
        f1.next()
        f2 = csv.reader(open(f_sustainedPLSRoffer, 'r'))
        f3 = csv.reader(open(f_sustainedTWDRoffer, 'r'))             
        f2.next()
        f2.next()
        f3.next()
        f3.next()
        r_tranches                = []
        r_prices                  = []
        r_quantities              = []
        r_tranch_nodes            = []
        for csv_offer in f1:
                if (csv_offer[0] == tp):
                        # Ignore offers on strategic nodes
                        if not(csv_offer[1] in strategic_nodes):
                                r_tranches.append(csv_offer[0]+" "+csv_offer[1]+" I"+csv_offer[2])
                                r_quantities.append( float(csv_offer[4]) )
                                sum_reserve = sum_reserve + float(csv_offer[4])  
                                csv_offer = f1.next()
                                r_prices.append( float(csv_offer[4]) )
                                r_tranch_nodes.append(csv_offer[1])        
        for csv_offer in f2:
                if (csv_offer[0] == tp):
                        # Ignore offers on strategic nodes
                        if not(csv_offer[1] in strategic_nodes):
                                r_tranches.append(csv_offer[0]+" "+csv_offer[1]+" P"+csv_offer[2])
                                r_quantities.append( float(csv_offer[4]) )
                                sum_reserve = sum_reserve + float(csv_offer[4])
                                csv_offer = f2.next()
                                csv_offer = f2.next()
                                r_prices.append( float(csv_offer[4]) )
                                r_tranch_nodes.append(csv_offer[1])     
        for csv_offer in f3:
                if (csv_offer[0] == tp):                       
                                # Ignore offers on strategic nodes
                        if not(csv_offer[1] in strategic_nodes) :
                                r_tranches.append(csv_offer[0]+" "+csv_offer[1]+" T"+csv_offer[2])
                                r_quantities.append( float(csv_offer[4]) )
                                sum_reserve = sum_reserve + float(csv_offer[4])
                                csv_offer = f3.next()
                                r_prices.append( float(csv_offer[4]) )
                                r_tranch_nodes.append(csv_offer[1])              
        return (dict(zip( r_tranches, zip(r_prices, r_quantities, r_tranch_nodes) )))


def Strategic_Consumer_Data():
        '''
        Returns the set of strategic nodes, with generator capacities
        , and generator cost function values.
        '''
        print "Setting strategic consumers..."
        strategic_nodes = ["TWI2201"]
        d_gen_cap = {} # consumer's capacity in each node
        r_gen_cap = {}
        for n in strategic_nodes:
                d_gen_cap[n] = 0.0
                r_gen_cap[n] = 0.0
                #demand[n] = 0
        d_gen_cap["TWI2201"]  = 100
        r_gen_cap["TWI2201"]  = 100
        gen_q = {}
        for n in strategic_nodes:
                gen_q[n] = [0.0]
        gen_q["TWI2201"]  = linspace(0, d_gen_cap["TWI2201"], 10)
        gen_c = {}
        for n in strategic_nodes:
                gen_c[n] = [0.0]
        gen_c["TWI2201"]  = polynomial(0.05, 20.0,100, gen_q["TWI2201"])       
        return ( strategic_nodes, d_gen_cap, gen_q, gen_c,r_gen_cap)

def polynomial(a, b, c, x):
        y = []
        for i in x:     
                y.append(c - a*i*i + b*i)
        return y

def Contract_Data(nodes, buses, beta, I, demands):
        '''
        Returns contract data
        '''
        print "Setting contract data..."
        strategic_retail_share          = 0.18
        strategic_industrial_share      = 0.18
        north_retail = 0.66                          # Percentage of retail demand in NI
        south_retail = 0.42                         # Percentage of retail demand in SI
        contracts = []
        contract_quantity = {}
        N = {}
        for n in nodes:
                contract_name = "CONTRACT_"+n
                contracts.append(contract_name)                
                island = Find_Island(buses, beta, n, I)
                if island == "NI":
                        amount = (demands[n] * strategic_retail_share     * north_retail 
                             + demands[n]  * strategic_industrial_share * (1.0-north_retail) )
                elif island == "SI":
                        amount = (demands[n] * strategic_retail_share     * south_retail 
                            + demands[n]  * strategic_industrial_share * (1.0-south_retail) )
                contract_quantity[contract_name] = amount
                N[contract_name] = n
        return (contracts, contract_quantity, N)

def Get_incumbent_data( f_incumbentvalues, n_scenarios):
        d_y     = {}
        scen  = []
        for tp in range(n_scenarios):
            d_y[tp]     = {}
        f = csv.reader(open(f_incumbentvalues, 'r'))
        f.next()
        for csv_value in f:
            d_y[int(csv_value[0])][int(csv_value[1])] = float(csv_value[2])
            scen.append(int(csv_value[1]))
        tots_cons = sum(d_y[i][scen[i]] for i in range(n_scenarios))
        return (d_y,scen,tots_cons)

def Get_incumbent_data_useus( f_incumbentvalues, n_scenarios):
        d_y     = {}
        scen  = []
        for tp in range(n_scenarios):
            d_y[tp]     = {}
        f = csv.reader(open(f_incumbentvalues, 'r'))
        f.next()
        for csv_value in f:
            d_y[int(csv_value[0])][int(csv_value[1])] = float(csv_value[2])
            scen.append(int(csv_value[1]))
        return (d_y,scen)


def Get_heu_incumbent_data( f_incumbentvalues, n_scenarios):
        d_y     = {}
        scen  = []
        for tp in range(n_scenarios):
            d_y[tp]     = {}
        f = csv.reader(open(f_incumbentvalues, 'r'))
        f.next()
        for csv_value in f:
            d_y[int(csv_value[0])][int(csv_value[1])] = float(csv_value[2])
            scen.append(int(csv_value[1]))
        tots_cons = sum(d_y[i][scen[i]] for i in range(n_scenarios))
        return (d_y,tots_cons)

def Set_incumbent_data(m,scen_no,d_y,d_pi,r_y,r_pi,d_y_val
                       ,d_pi_val,r_y_val,r_pi_val,strategic_nodes,buses,beta,I,islands):
    for n in strategic_nodes:
        m.addConstr( d_y[n] -  d_y_val[0] ,GRB.EQUAL,0 ,"fix_incumbent_d_y_%s_%s" %(scen_no,n))
        m.addConstr( d_pi[n] - d_pi_val[0],GRB.EQUAL,0  , "fix_incumbent_d_pi_%s_%s" %(scen_no,n))
        m.addConstr( r_y[n] -  r_y_val[0] ,GRB.EQUAL,0 , "fix_incumbent_r_y_%s_%s" %(scen_no,n))
        for l in islands:
            if Find_Island(buses, beta, n , I)==l:
                m.addConstr( r_pi[l] - r_pi_val[0] ,GRB.EQUAL,0,  "fix_incumbent_r_pi_%s_%s" %(scen_no,n))

def Set_half_incumbent_data(m,scen_no,d_y,d_y_val,strategic_nodes):
    for n in strategic_nodes:
        m.addConstr( d_y[n] -  d_y_val ,GRB.EQUAL,0 ,"fix_incumbent_d_y_%s_%s" %(scen_no,n))
def Set_semi_incumbent_data(m,scen_no,d_y,d_pi,r_y,d_y_val,d_pi_val,r_y_val,strategic_nodes):
    for n in strategic_nodes:
        m.addConstr( d_y[n] -  d_y_val[0] ,GRB.EQUAL,0 ,"fix_incumbent_d_y_%s_%s" %(scen_no,n))
        m.addConstr( d_pi[n] - d_pi_val[0],GRB.EQUAL,0  , "fix_incumbent_d_pi_%s_%s" %(scen_no,n))
        m.addConstr( r_y[n] -  r_y_val[0] ,GRB.EQUAL,0 , "fix_incumbent_r_y_%s_%s" %(scen_no,n))

def Set_price_incumbent_data(m,scen_no,d_pi,r_pi,d_pi_val,r_pi_val
    ,strategic_nodes,buses,beta,I,islands):
    for n in strategic_nodes:
        m.addConstr( d_pi[n] - d_pi_val[0],GRB.EQUAL,0  
                , "fix_incumbent_d_pi_%s_%s" %(scen_no,n))   
        for l in islands:
            if Find_Island(buses, beta, n , I)==l:
                m.addConstr( r_pi[l] - r_pi_val[0] ,GRB.EQUAL,0, 
                         "fix_incumbent_r_pi_%s_%s" %(scen_no,n))


def Get_TP_Data(f_tp):
    f = csv.reader(open(f_tp, 'r'))
    f.next()
    for csv_value in f:
        length_n_of_days = float(csv_value[0])
        ave_cons = float(csv_value[1])
        n_of_weeks = float(csv_value[2])
        max_utility = float(csv_value[3])
        n_day_tps = float(csv_value[4])
        days_of_week = float(csv_value[5])
        days_set = float(csv_value[6])
        start_date = float(csv_value[7])
        n_tps = float(csv_value[8])
    timeperiod_type = []
    scenarios = {}
    timeperiod = {}
    dates = {}
    for day_no in range(days_of_week):
        timeperiod[day_no] = {}
        dates[day_no] = []
    for tp_count in range(n_day_tps):
        timeperiod_type.append((datetime.datetime(start_date) 
                    + datetime.timedelta(minutes = 30*tp_count)).time())
        scenarios[timeperiod_type[tp_count]] = []
    for dy in range(length_n_of_days):
        dat = datetime.datetime(start_date)+ datetime.timedelta(days = dy)
        day_no = dat.weekday()  
        dates[day_no].append(dat)
    for day_no in range(days_of_week):                          
        for wday in dates[day_no]:
            timeperiod[day_no][wday] = []
            for tp_count in range(n_day_tps):
                timeperiod[day_no][wday].append(wday + datetime.timedelta(minutes = 30*tp_count))
    for tp_count in range(n_tps):
        for tp in timeperiod:
            if tp.time() == timeperiod_type[tp_count]:
                scenarios[timeperiod_type[tp_count]].append(tp)            
        return(length_n_of_days,ave_cons,n_of_weeks,max_utility
               ,n_day_tps,days_of_week,days_set,start_date
               ,timeperiod_type,scenarios,timeperiod,dates,n_tps)

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

def Get_Range_Data():
    numberOf_tp = 48
    dem_levels = [300,500,700]
    folder = "dataset_1"
    return(numberOf_tp,dem_levels,folder)


def main():
    
    print "Getting data"

if __name__ == "__main__":
        main()


