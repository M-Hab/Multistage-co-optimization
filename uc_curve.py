
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
import get_data

ZERO = 1e-5
utility_step = 0.01
stage_dep = 1
max_utility = 100

def Make_uc(max_utility,n_tps,rhos,f_uc):

        # The expected values of consumption and utility in each TP
        d_y_total = {}
        d_p_total = {}
        utility_total = {}
        # The aggregated future expected values of consumption 
        #and utility with that of the current scenario in current tp
        d_y_agg = {}
        utility_agg = {}
        d_y_agg_big = {}
        utility_agg_big = {}
        # The lists that make the plot of u-dem curve for each scenario in each TP
        utility_list= {}
        d_y_list ={}    
        # The lists that has all the points of the corner points 
        # (with duplicates) total expected u-dem curve for each TP 
        tot_utility_list= {}
        tot_d_y_list= {}  
        # The lists of the expected utility dem curves with the duplicates 
        # eliminated and only the starting points of each vertical part
        unique_tot_utility_list= {}
        unique_tot_d_y_list= {}
        # The lists that make the plot of the total expected u-dem curve for each TP 
        plot_unique_tot_utility_list= {}  
        plot_unique_tot_d_y_list= {}                   
        #Getting data
        (d_y, d_p, utility,clusters)=Get_uc_data(f_uc, n_tps)
        # We start backwards from the last time period
        for tp in range(n_tps-1,-1,-1):
            #Making dicts for each TP
            d_y_agg[tp] = {}
            utility_agg[tp] = {}
            d_y_agg_big[tp] = {}
            utility_agg_big[tp] = {}
            d_y_total[tp] ={}
            d_p_total[tp] = {}
            utility_total[tp] = {}
            utility_list[tp]= {}
            d_y_list[tp] ={}
            #Making lists for each TP
            tot_utility_list[tp]= {}
            tot_d_y_list[tp]= {}
            unique_tot_utility_list[tp]= {}
            unique_tot_d_y_list[tp]= {}
            plot_unique_tot_utility_list[tp]= {}
            plot_unique_tot_d_y_list[tp]= {}
            for j_b in clusters[tp-1]:
                tot_utility_list[tp][j_b]= []
                tot_d_y_list[tp][j_b]= []
                unique_tot_utility_list[tp][j_b]= []
                unique_tot_d_y_list[tp][j_b]= []
                plot_unique_tot_utility_list[tp][j_b]= []
                plot_unique_tot_d_y_list[tp][j_b]= []
            #If it is the last time period
            if tp == n_tps-1:
                for j in clusters[tp]: 
                    #Making dicts for each scenario
                    utility_total[tp][j]= {}
                    d_y_total[tp][j] ={}
                    utility_list[tp][j]= []
                    d_y_list[tp][j] =[]
                    for j_b in clusters[tp-1]:
                        #Making dicts for each scenario
                        utility_total[tp][j][j_b]= {}
                        d_y_total[tp][j][j_b] ={}
                        #For each  consumption level in each scenario 
                        #we find the expected utility over all scenarios  
                        for k in range(len( d_y[tp][j])):
                            utility_total[tp][j][j_b][k] = 0
                            utility_total[tp][j][j_b][k]= utility_total[tp][j][j_b][k] + utility[
                                tp][j][k]*rhos[tp-1][(j_b,j)]
                            #Counts the number of utility levels found to get the expected  value,
                            # if we get the expected over fewer number of scenarios
                           # it means that for some scenarios we need get the max utility.
                            count = 0
                            for l in clusters[tp]:
                                if l != j :
                                    for k_l in range(len(d_y[tp][l])):
                        #In each scenario "l" other than the selected scenario "j"
                        # look for the first consumption level "k_l" which is 
                        # equal or more than the current scenarios "K" consumption level  and add the
                        #weighted utility
                                        if d_y[tp][j][k] <= d_y[tp][l][k_l]:
                                            utility_total[tp][j][j_b][k]=utility_total[
                                            tp][j][j_b][k] + utility[tp][l][k_l]*(
                                            rhos[tp-1][(j_b,l)])
                                            count = count + 1
                                            break             
                            # For those scenarios which did not have a point with consumption level
                            # more than that of scenario j, we add a weighted max utility                                                             
                            if count < (len(clusters[tp]) - 1):
                               utility_total[tp][j][j_b][k]=utility_total[tp][j][j_b][k] 
                               +(len(clusters[tp])-count-1)*max_utility*(
                               rhos[tp-1][(j_b,j)])
                for j in clusters[tp]: 
                    for k in range(len( d_y[tp][j])):
                # As we only have the starting point of each vertical part, 
                # the las point of the vertical part is added to make the plots, to do this:
                        # First we add all the points for each scenario to a list to make the plot
                        d_y_list[tp][j].append(d_y[tp][j][k])
                        utility_list[tp][j].append(utility[tp][j][k]) 
            #Then we add another point at each consumption level to make the vertical parts
                        if k < len( d_y[tp][j])-1:
                            utility_list[tp][j].append(utility[tp][j][k+1]-utility_step) 
                            d_y_list[tp][j].append(d_y[tp][j][k])
        #If it is the last point and it is not already at the max utility, 
        # a new point with the max utility is added to the plot
                        else:
                            if   utility[tp][j][k] !=  max_utility :                      
                                utility_list[tp][j].append(max_utility ) 
                                d_y_list[tp][j].append(d_y[tp][j][k])                                                 
#make the list to plot the total expected curve for current tp                                                                                                 
                for j in clusters[tp]: 
                    for j_b in clusters[tp-1]:
                        for k in range(len( d_y[tp][j])):
                            tot_utility_list[tp][j_b].append(
                            round(utility_total[tp][j][j_b][k],1))
                            tot_d_y_list[tp][j_b].append(d_y[tp][j][k])       
# Sort the list   
                for j_b in clusters[tp-1]:                            
                    sort_list  = zip( tot_utility_list[tp][j_b],tot_d_y_list[tp][j_b]  )
                    list.sort(sort_list)
                    (tot_utility_list[tp][j_b],tot_d_y_list[tp][j_b]  ) = zip(*sort_list)  
 #remove the duplicates:
 # Add the first point                            
                    for item in range(len(tot_d_y_list[tp][j_b]) -1):
                        if item ==0:
                            unique_tot_d_y_list[tp][j_b].append(tot_d_y_list[tp][j_b][item])
                            unique_tot_utility_list[tp][j_b].append(tot_utility_list[tp][j_b][item])
    # if the point has a unique consumption level it is added to the list
                        if ( (tot_d_y_list[tp][j_b][item] != tot_d_y_list[tp][j_b][item+1])
                            and (tot_utility_list[tp][j_b][item] != tot_utility_list[tp][j_b][item+1])):
                            unique_tot_d_y_list[tp][j_b].append(tot_d_y_list[tp][j_b][item+1])
                            unique_tot_utility_list[tp][j_b].append(tot_utility_list[tp][j_b][item+1])
                    if unique_tot_d_y_list[tp][j_b][len(unique_tot_d_y_list[tp][j_b])-1] != 800:
                        unique_tot_d_y_list[tp][j_b][len(unique_tot_d_y_list[tp][j_b])-1] = 800

## Make a list to plot the total expected values with none of the duplicates and with vertical sections:
## First we make a list equavalent to the nodes we have
#                    plot_unique_tot_d_y_list[tp][j_b] = unique_tot_d_y_list[tp][j_b]
#                    plot_unique_tot_utility_list[tp][j_b] = unique_tot_utility_list[tp][j_b]
# # For any point we make another point with the same consumption level 
# #and the utility of one unite less than the next point
#                    for y1 in range(len(unique_tot_d_y_list[tp][j_b])-1):
# # If the point that we want to add will have a more utility as we already have for the current point
#                        if (unique_tot_utility_list[tp][j_b][y1+1]- utility_step
#                            > unique_tot_utility_list[tp][j_b][y1]):
#                            plot_unique_tot_d_y_list[tp][j_b].append(
#                                unique_tot_d_y_list[tp][j_b][y1])
#                            plot_unique_tot_utility_list[tp][j_b].append(
#                            unique_tot_utility_list[tp][j_b][y1+1] - utility_step)
## Sort the lists
#                    sort_list  = zip( plot_unique_tot_utility_list[tp][j_b] 
#                    ,plot_unique_tot_d_y_list[tp][j_b] )
#                    list.sort(sort_list)
#                    (plot_unique_tot_utility_list[tp][j_b]
#                  ,plot_unique_tot_d_y_list[tp][j_b]  ) = zip(*sort_list)                                    
                    sort_list  = zip( unique_tot_utility_list[tp][j_b],unique_tot_d_y_list[tp][j_b]  )
                    list.sort(sort_list)
                    (unique_tot_utility_list[tp][j_b],unique_tot_d_y_list[tp][j_b] ) = zip(*sort_list)   
##Plot                                                                                                                                                      
                #for j in clusters[tp]:                        
                #        plt.figure(tp)
                #        plt.subplot(211)
                #        plt.plot( d_y_list[tp][j] ,utility_list[tp][j])
                #for j_b in clusters[tp-1]: 
                #    plt.subplot(212)
                #    plt.plot(plot_unique_tot_d_y_list[tp][j_b], plot_unique_tot_utility_list[tp][j_b])
                #plt.show()
                #for j in clusters[tp]: 
                #    fig = plt.figure(tp)
                #    plt.subplot(211)
                #    ax = Axes3D(fig)                   
                #    ax.scatter(d_y[tp][j], utility[tp][j],  d_p[tp][j], zdir='z')
                #    Axes3D.plot_surface(d_y[tp][j], utility[tp][j], d_p[tp][j])
                #    surf = ax.plot_surface(d_y[tp][j], utility[tp][j], d_p[tp][j])
                #    fig.colorbar(surf, shrink=0.5, aspect=5)
                for j in clusters[tp]: 
                    with open('uc_cluster.csv', 'ab') as fp2:
                        all2 = csv.writer(fp2)
                        for i in range(len(d_y_list[tp][j])):
                            all2.writerow([str(tp),j,d_y_list[tp][j][i],utility_list[tp][j][i]])                        
                    #plt.figure(tp)
                    #plt.subplot(211)
                    #plt.plot( d_y_list[tp][j] ,utility_list[tp][j])
                for j_b in clusters[tp-1]: 
                    with open('uc_tp.csv', 'ab') as fp3:
                        all3 = csv.writer(fp3)
                        for i in range(len(unique_tot_d_y_list[tp][j_b])):
                            all3.writerow([str(tp),j_b,unique_tot_d_y_list[tp][j_b][i],unique_tot_utility_list[tp][j_b][i]]) 

#For the TPs other than the last one
            else:
                for j in clusters[tp]:  
                    #We make dicts of the aggregated dem-u curves of current scenario
                    #and future expected values for each scenario   
                    d_y_agg[tp][j] = []
                    d_y_agg_big[tp][j] = []
                    utility_agg[tp][j] = []
                    utility_agg_big[tp][j] = []

                    for ten_u in range(0,10000):
                        u = round(ten_u*0.1,2)
                        for f in range(len(unique_tot_utility_list[tp+1][j])):
                            if f < len(unique_tot_utility_list[tp+1][j]) -1 :
                                if u >= unique_tot_utility_list[tp+1][j][f] and u < unique_tot_utility_list[tp+1][j][f+1] :
                                    for k in  range(len(utility[tp][j])):
                                        if k < len(utility[tp][j]) - 1:
                                            if u >= utility[tp][j][k] and u < utility[tp][j][k+1]:

                                                d_y_agg_big[tp][j].append(d_y[tp][j][k] + unique_tot_d_y_list[tp+1][j][f])
                                                utility_agg_big[tp][j].append(u)
                                                break_f = 1
                                                break
                                        else:
                                            if u >= utility[tp][j][k]:
                                                d_y_agg_big[tp][j].append(d_y[tp][j][k] + unique_tot_d_y_list[tp+1][j][f])
                                                utility_agg_big[tp][j].append(u)
                                                break_f = 1
                                                break

                            else:
                                if u >= unique_tot_utility_list[tp+1][j][f]:
                                    for k in  range(len(utility[tp][j])):
                                        if k < len(utility[tp][j]) - 1:
                                            if u >= utility[tp][j][k] and u < utility[tp][j][k+1]:
                                                d_y_agg_big[tp][j].append(d_y[tp][j][k] + unique_tot_d_y_list[tp+1][j][f])
                                                utility_agg_big[tp][j].append(u)
                                                break_f = 1
                                                break
                                        else:
                                            if u >= utility[tp][j][k]:
                                                d_y_agg_big[tp][j].append(d_y[tp][j][k] + unique_tot_d_y_list[tp+1][j][f])
                                                utility_agg_big[tp][j].append(u)
                                                break_f = 1
                                                break
                            if break_f ==1 :
                                break_f =0
                                break                                     

                                
                    for index_y in range(len(d_y_agg_big[tp][j])):
                        if index_y == 0:
                            d_y_agg[tp][j].append(d_y_agg_big[tp][j][index_y])
                            utility_agg[tp][j].append(utility_agg_big[tp][j][index_y])
                        else:
                            if d_y_agg_big[tp][j][index_y] != d_y_agg_big[tp][j][index_y-1]:
                                d_y_agg[tp][j].append(d_y_agg_big[tp][j][index_y])
                                utility_agg[tp][j].append(utility_agg_big[tp][j][index_y])

####duplicate start

#                    #For each point in each scenario's u-dem curves
#                    for k in range(len(utility[tp][j])):
#                        # And each point in the future dem-u curve
#                        for u in range(len(unique_tot_utility_list[tp+1][j])):                                         
##If the current scenario's point's utiity is equal to the point chosen from the future dem-u:
#                            if (utility[tp][j][k] == unique_tot_utility_list[tp+1][j][u]):
## we add the respective consumption values 
##at the given utility and add it to the d_y list     
#                                    d_y_agg[tp][j].append(d_y[tp][j][k] + unique_tot_d_y_list[tp+1][j][u])
#                                    #We add the utility level to utility list
#                                    utility_agg[tp][j].append(utility[tp][j][k])
#                                    #We go on to the next point
#                                    continue
#                            if  (u < len(unique_tot_utility_list[tp+1][j]) - 1):     
#                                #If the point in future curve is not the last point:                                                             
#                                if (utility[tp][j][k] > unique_tot_utility_list[tp+1][j][u] 
#                                    and utility[tp][j][k] < unique_tot_utility_list[tp+1][j][u+1]):
#                        #If the utility of the chosen point from current scenario is in between
#                        #the utilities of two points the future's curve:
#                                    # We add the sum of consumptio level of the chosen node from c
#                                    #urrent scenario and that of the point
#                                    #of the future curve at its left side "u" to the list
#                                    d_y_agg[tp][j].append(d_y[tp][j][k] + unique_tot_d_y_list[tp+1][j][u])
#                                    # We add the utility level of crrent scen's point to the list 
#                                    utility_agg[tp][j].append(utility[tp][j][k])
#                                    #We go on to the next point
#                                    continue
#                            if (k < len(utility[tp][j]) - 1) : 
##If the utility of the chosen point is in between the utilities 
##of two points the current scenario's curve:
#                                if (utility[tp][j][k+1] > unique_tot_utility_list[tp+1][j][u] 
#                                    and utility[tp][j][k] < unique_tot_utility_list[tp+1][j][u]):
## We add the sum of consumptio level of the chosen node from future curve 
##and that of the point of the current scenario "k" to the list                                    
#                                    d_y_agg[tp][j].append(d_y[tp][j][k] 
#                                    + unique_tot_d_y_list[tp+1][j][u])
## We add the utility level of the chosen point of the future curve to the list  
#                                    utility_agg[tp][j].append(unique_tot_utility_list[tp+1][j][u])
##We go on to the next point
#                                    continue
#                                #If the point in future curve is the last point:   
#                            if (u >= len(unique_tot_utility_list[tp+1][j]) - 1):
#                                    if (utility[tp][j][k] > unique_tot_utility_list[tp+1][j][u] 
#                                        and utility[tp][j][k] < max_utility):
#                                        d_y_agg[tp][j].append(d_y[tp][j][k] 
#                                           + unique_tot_d_y_list[tp+1][j][u])
#                                        utility_agg[tp][j].append(utility[tp][j][k])
#                                        continue
#                                #If the point in current scenario is the last point:  
#                            if (k >= len(utility[tp][j]) - 1): 
#                                    if (utility[tp][j][k] < unique_tot_utility_list[tp+1][j][u] 
#                                        and unique_tot_utility_list[tp+1][j][u] <= max_utility):
#                                        d_y_agg[tp][j].append(
#                                            d_y[tp][j][k] + unique_tot_d_y_list[tp+1][j][u])
#                                        utility_agg[tp][j].append(
#                                            unique_tot_utility_list[tp+1][j][u])        

####duplicate end
                                                              
#We make the lists to plot them in the same way as the last TP,
# the only difference is that we use the agg lists.
                for j in clusters[tp]:
                    utility_total[tp][j]= {}
                    d_y_total[tp][j] ={}
                    for j_b in clusters[tp-1]:                      
                        utility_total[tp][j][j_b]= {}
                        d_y_total[tp][j][j_b] ={}
                    utility_list[tp][j]= []
                    d_y_list[tp][j] =[]
                    #Making the expected curve
                    for j_b in clusters[tp-1]: 
                        for k in range(len( d_y_agg[tp][j])):
                            utility_total[tp][j][j_b][k] = 0
                            if tp != 0:
                                utility_total[tp][j][j_b][k]= (
                                    utility_total[tp][j][j_b][k] 
                                +utility_agg[tp][j][k]*rhos[tp-1][(j_b,j)])
                            if tp == 0:
                                utility_total[tp][j][j_b][k]= (
                                    utility_total[tp][j][j_b][k] 
                                +utility_agg[tp][j][k]*rhos[tp-1][(j_b,j)])
                            count = 0
                            for l in clusters[tp]:
                                if l != j :
                                    for k_l in range(len(d_y_agg[tp][l])):
                                        if d_y_agg[tp][j][k] <= d_y_agg[tp][l][k_l]:
                                            if tp != 0:
                                                utility_total[tp][j][j_b][k]=(
                                                    utility_total[tp][j][j_b][k]+utility_agg[
                                                        tp][l][k_l]*(rhos[tp-1][(j_b,l)]))
                                            if tp == 0:
                                                utility_total[tp][j][j_b][k]=(
                                                    utility_total[tp][j][j_b][k] 
                                                +utility_agg[tp][l][k_l]*(
                                                 rhos[tp-1][(j_b,l)]))
                                            count = count + 1
                                            break 
                            if count <= len(clusters[tp]) - 1:
                                if tp != 0:
                                    utility_total[tp][j][j_b][k]=(
                                        utility_total[tp][j][j_b][k] + (
                                            len(clusters[tp])-count-1)*(
                                                max_utility-utility_step)*rhos[tp-1][(j_b,j)])
                                if tp == 0:
                                    utility_total[tp][j][j_b][k]=(
                                        utility_total[tp][j][j_b][k] + (
                                            len(clusters[tp])-count-1)*(
                                                max_utility-utility_step)*rhos[tp-1][(j_b,j)])                            
            #Making the lists for the expected curve to plot it
                    for k in range(len( d_y_agg[tp][j])):
                        utility_list[tp][j].append(utility_agg[tp][j][k])
                        d_y_list[tp][j].append(d_y_agg[tp][j][k])
                        if k < len( d_y_agg[tp][j])-1:
                            if utility_agg[tp][j][k+1]-utility_step > utility_agg[tp][j][k]:
                                utility_list[tp][j].append(utility_agg[tp][j][k+1]-utility_step) 
                                d_y_list[tp][j].append(d_y_agg[tp][j][k])
                        if k >= (len( d_y_agg[tp][j])-1):
                            if utility_agg[tp][j][k] < max_utility - utility_step :
                                utility_list[tp][j].append(max_utility - utility_step )
                                d_y_list[tp][j].append(d_y_agg[tp][j][k])                                                                                      
    # Make the lists to make each scenarios aggregated curve
                for j_b in clusters[tp-1]:  
                    for j in clusters[tp]:                                                                             
                        for k in range(len( d_y_agg[tp][j])):
                            tot_utility_list[tp][j_b].append(round(utility_total[tp][j][j_b][k] , 1))
                            #tot_utility_list[tp][j_b].append(utility_total[tp][j][j_b][k] )
                            tot_d_y_list[tp][j_b].append(d_y_agg[tp][j][k])       
#Sorting the list to plot is
                    sort_list  = zip( tot_utility_list[tp][j_b] ,tot_d_y_list[tp][j_b] )
                    list.sort(sort_list)
                    ( tot_utility_list[tp][j_b],tot_d_y_list[tp][j_b]) = zip(*sort_list) 
# Remove the duplicates and points with equal consumption levels from the lists
                    for item in range(len(tot_d_y_list[tp][j_b]) -1):
                            if item ==0:
                                unique_tot_d_y_list[tp][j_b].append(tot_d_y_list[tp][j_b][item])
                                unique_tot_utility_list[tp][j_b].append(
                                    tot_utility_list[tp][j_b][item])
                            if ((tot_d_y_list[tp][j_b][item] != tot_d_y_list[tp][j_b][item+1]) and (
                                tot_utility_list[tp][j_b][item] != tot_utility_list[tp][j_b][item+1])):
                                unique_tot_d_y_list[tp][j_b].append(tot_d_y_list[tp][j_b][item+1])
                                unique_tot_utility_list[tp][j_b].append(
                                    tot_utility_list[tp][j_b][item+1])

                    if unique_tot_d_y_list[tp][j_b][len(unique_tot_d_y_list[tp][j_b])-1] != 800*(n_tps-tp):
                        unique_tot_d_y_list[tp][j_b][len(unique_tot_d_y_list[tp][j_b])-1] = 800*(n_tps-tp)


    ## Make vertical parts by adding an extra point to consumption level, 
    ##if only the length of the vertical part is going to be more than a utility_step
    #                plot_unique_tot_d_y_list[tp][j_b] = unique_tot_d_y_list[tp][j_b]
    #                plot_unique_tot_utility_list[tp][j_b] = unique_tot_utility_list[tp][j_b]
    #                for y1 in range(len(unique_tot_d_y_list[tp][j_b])-1):
    #                    if unique_tot_utility_list[tp][j_b][y1] < (
    #                        unique_tot_utility_list[tp][j_b][y1+1]- utility_step) :
    #                        plot_unique_tot_d_y_list[tp][j_b].append(
    #                            unique_tot_d_y_list[tp][j_b][y1])
    #                        plot_unique_tot_utility_list[tp][j_b].append( 
    #                            unique_tot_utility_list[tp][j_b][y1+1] - utility_step)
    ##Sorting lists
    #                sort_list  = zip( plot_unique_tot_utility_list[tp][j_b]
    #                                 ,plot_unique_tot_d_y_list[tp][j_b]  )
    #                list.sort(sort_list)
    #                (plot_unique_tot_utility_list[tp][j_b],plot_unique_tot_d_y_list[tp][j_b] ) = zip(*sort_list)                                    
                    sort_list  = zip( unique_tot_utility_list[tp][j_b] ,unique_tot_d_y_list[tp][j_b] )
                    list.sort(sort_list)
                    ( unique_tot_utility_list[tp][j_b] ,unique_tot_d_y_list[tp][j_b]) = zip(*sort_list)                               
#Make the plots                                                            
                for j in clusters[tp]: 
                    with open('uc_cluster.csv', 'ab') as fp2:
                        all2 = csv.writer(fp2)
                        for i in range(len(d_y_list[tp][j])):
                            all2.writerow([str(tp),j,d_y_list[tp][j][i],utility_list[tp][j][i]])                        
                    #plt.figure(tp)
                    #plt.subplot(211)
                    #plt.plot( d_y_list[tp][j] ,utility_list[tp][j])
                for j_b in clusters[tp-1]: 
                    with open('uc_tp.csv', 'ab') as fp3:
                        all3 = csv.writer(fp3)
                        for i in range(len(unique_tot_d_y_list[tp][j_b])):
                            all3.writerow([str(tp),j_b,unique_tot_d_y_list[tp][j_b][i],unique_tot_utility_list[tp][j_b][i]]) 
                #    plt.subplot(212)
                #    plt.plot(plot_unique_tot_d_y_list[tp][j_b], plot_unique_tot_utility_list[tp][j_b])
                #plt.show()
        return(d_y,utility,d_y_list,utility_list,unique_tot_d_y_list,unique_tot_utility_list)
def Get_uc_data(f_plot, n_tps):

    d_y     = {}
    d_p     = {}
    utility = {}
    clusters={}
    clusters[-1] = '0'
    for tp in range(n_tps):
        clusters[tp] = []
        d_y[tp]     = {}
        d_p[tp]    = {}
        utility[tp] = {}
        f = csv.reader(open(f_plot, 'r'))
        for csv_value in f:
            if int(csv_value[1]) == tp: 
                if csv_value[2] not in clusters[tp] :
                    clusters[tp].append(csv_value[2])
                    d_y[tp][csv_value[2]]= []
                    d_p[tp][csv_value[2]] = []
                    utility[tp][csv_value[2]] = []
                d_y[tp][csv_value[2]].append(float(csv_value[3]))
                d_p[tp][csv_value[2]].append(float(csv_value[4]))
                utility[tp][csv_value[2]].append(float(csv_value[0]))
       
    return (d_y,d_p,utility,clusters)

def Get_rho_data(n_tps,f_rho):

    rhos={}
    for tp in range(-1,n_tps):
        rhos[tp] = {}
        f = csv.reader(open(f_rho, 'r'))
        for csv_value in f:
            if int(csv_value[0]) == tp: 
                rhos[tp][(csv_value[1],csv_value[2])] = float(csv_value[3])
    return rhos   
             
def main():
    (n_tps,dem_levels,sample) =  get_data.Get_Range_Data()
    rhos = Get_rho_data(n_tps,'rho_%s.csv'%sample)
    (scen_y, scen_u , tot_y_list , tot_u_list,unique_d_y_list,unique_utility_list) = Make_uc(max_utility,n_tps,rhos,'bisection_uc_data.csv')

if __name__ == "__main__":
        main()
