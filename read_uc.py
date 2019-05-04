
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
import cluster
import uc_data
import get_data
import  uc_curve

ZERO = 1e-5
utility_step = 0.01
stage_dep = 1
max_utility = 100
def Get_curve_data(n_tps,f_curve):

    y_list={}
    u_list={}
    for tp in range(n_tps):
        y_list[tp]={}
        u_list[tp]={}
        f = csv.reader(open(f_curve, 'r'))
        for csv_value in f:
            if int(csv_value[0]) == tp: 
                if csv_value[1] not in y_list[tp].keys():
                    y_list[tp][csv_value[1]]= [float(csv_value[2])]
                    u_list[tp][csv_value[1]]= [float(csv_value[3])]
                else:
                    y_list[tp][csv_value[1]].append(float(csv_value[2]))
                    u_list[tp][csv_value[1]].append(float(csv_value[3]))
    return (y_list , u_list)   
 
def Reading_uc(os_cluster,tot_y_list,tot_u_list,ctg,tp):
    y_list = []
    u_list = []
    if os_cluster in tot_y_list.keys():
        y_list = tot_y_list[os_cluster]
        u_list = tot_u_list[os_cluster]
    else:
        for i in range(len(os_cluster)-1,0,-1):
            found_cluster = False
            temp_clusters = []
            c_steps= []
            part1 = os_cluster[:i] 
            part2 = os_cluster[i:] 
            if len(part2)>1 :
                for i in [10,-10,11,-11,9,-9,12,-12,8,-8]:
                    c_steps.append(i)
            else :
                for i in [1,-1]:
                    c_steps.append(i)
            for c_step in c_steps:
                temp_clusters.append(part1+str(int(part2)+c_step))

            for temp_cluster in temp_clusters:
                if temp_cluster in tot_y_list.keys():
                    y_list = tot_y_list[temp_cluster]
                    u_list = tot_u_list[temp_cluster]
                    found_cluster = True
                    break
            if found_cluster:
                break

    chosen_u = -1
    for i in range(len(y_list)):
        if chosen_u != -1 :
            break
        if y_list[i] >= ctg:
            chosen_u = u_list[i]
            if chosen_u == max_utility:
                chosen_u = max_utility*2
    if chosen_u == -1:
        print "error"
    with open('chosen_u.csv', 'ab') as fp08:
            all08 = csv.writer(fp08)
            all08.writerow([str(tp),str(ctg),str(chosen_u)])
    return(chosen_u)

def Calculate_cost(d_y,r_y,d_p,r_p,total_cost):
    current_cost = d_p*d_y-r_y*r_p 
    total_cost = total_cost + current_cost
    return(current_cost,total_cost)

def main():

    (n_tps,dem_levels,sample) =  get_data.Get_Range_Data()

    (tot_y_list , tot_u_list) = Get_curve_data(n_tps,"uc_cluster.csv")
    (unique_d_y_list,unique_utility_list) = Get_curve_data(n_tps,"uc_tp.csv")
    ##or 
    #rhos = Get_rho_data(n_tps,'rho_data.csv')   
    #(tot_y_list , tot_u_list,unique_d_y_list,unique_utility_list) = uc_curve.Make_uc(max_utility,n_tps,rhos,'bisection_uc_data_fixed.csv')
        
    sample = "outofsample"
    ave_consumption = 572
    total_consumption = ave_consumption*n_tps
    outofsample_dates_list = []
    outofsample_price_dict = {}
    outofsample_cluster_dict = {}
    for root, dirs, files in os.walk("./"+sample):  
        for dirname in dirs:
            outofsample_dates_list.append(dirname)    
    for sc in range(n_tps):
        outofsample_price_dict[sc] ={} 
        outofsample_cluster_dict[sc] = {}
        for date in outofsample_dates_list:
            outofsample_price_dict[sc][date] = "" 
            (outofsample_price_dict,outofsample_cluster_dict)=cluster.Dispatch("./"+sample+"/"+date+"/",sc,dem_levels,outofsample_price_dict,outofsample_cluster_dict,date,sample)
    with open('total_cost.csv', 'ab') as fp07:
            all07 = csv.writer(fp07)
            all07.writerow(['sample','U-C','fixed'])
    with open('tp_cost.csv', 'ab') as fp09:
            all09 = csv.writer(fp09)
            all09.writerow(['sample','TP','U-C','fixed'])
    for os_date in outofsample_dates_list:
        ctg = total_consumption
        total_cost = 0
        cost = {}
        fixed_total_cost = 0
        fixed_cost = {}
        os_d_y ={}
        fixed_d_y = {}
        os_d_p  = {}
        fixed_d_p = {}
        os_r_y = {}
        fixed_r_y = {}
        os_r_p = {}
        fixed_r_p = {}

        for tp in range(n_tps):
            os_cluster = outofsample_price_dict[tp][os_date]
            os_u = Reading_uc(os_cluster,tot_y_list[tp],tot_u_list[tp],ctg,tp)        
            (os_d_y[tp],os_d_p[tp],os_r_y[tp],os_r_p[tp])= uc_data.S_MIP(tp,os_cluster,["./"+sample+"/"+os_date+"/"],0,0,0,0,0,os_u,0, 0,sample,mip_gap = 0.000001,fixed_cons = 'NA')
            ctg  = ctg - os_d_y[tp]
            (cost[tp],total_cost) = Calculate_cost(os_d_y[tp],os_r_y[tp],os_d_p[tp],os_r_p[tp],total_cost)

            (fixed_d_y[tp],fixed_d_p[tp],fixed_r_y[tp],fixed_r_p[tp])= uc_data.S_MIP(tp,os_cluster,["./"+sample+"/"+os_date+"/"],0,0,0,0,0,0,0, 0,sample,mip_gap = 0.000001,fixed_cons = ave_consumption )
            (fixed_cost[tp],fixed_total_cost) = Calculate_cost(fixed_d_y[tp],fixed_r_y[tp],fixed_d_p[tp],fixed_r_p[tp],fixed_total_cost)

        for tp in range(n_tps):
            with open('tp_cost.csv', 'ab') as fp09:
                    all09 = csv.writer(fp09)
                    all09.writerow([os_date,str(tp),str(cost[tp]),str(fixed_cost[tp])])
        with open('total_cost.csv', 'ab') as fp07:
                all07 = csv.writer(fp07)
                all07.writerow([os_date,str(total_cost),str(fixed_total_cost)])

if __name__ == "__main__":
        main()
