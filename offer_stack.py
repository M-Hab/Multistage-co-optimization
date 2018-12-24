##
#   offer_stack.py
#
import random as random
import numpy as numpy
import csv as csv
from pprint import pprint
from pulp import *

def main():
    
    print GenerateProbabilities(4)


def ReadOfferDataTXT(file_name):
    '''
    Reads price and quantity data from a txt file containing
    offer stack data. At the moment takes all offers in the file,
    not for a single time period. Does not keep track of which 
    company submitted which offer.

    INPUTS:     file_name   - name of file.
    RETURNS:    price       - unsorted list of prices
                quantity    - unsorted list of quantities
    '''
    f = open(file_name, 'r')
    tranches = []
    price = []
    quantity = []
    for line in iter(f):
        values = line.split()
        tranches.append(values[0])
        price.append(float(values[1]))
        quantity.append(float(values[2]))
    f.close()
    return (tranches, price, quantity)

def ReadOfferDataCSV(file_name):
    '''
    Reads price and quantity data from a csv file containing
    offer stack data. At the moment takes all offers in the file,
    not for a single time period. Does not keep track of which 
    company submitted which offer.

    INPUTS:     file_name   - name of file.
    RETURNS:    price       - unsorted list of prices
                quantity    - unsorted list of quantities
    '''
    f = csv.reader(open(file_name, 'rb'))
    header = f.next()

    quantity = []
    price = []
    tranches = []
    data = []

    j=0
    for line in f:
        data.append(line)
        # Create identifying tranch for each p, q.
        for i in range(5):
        # TODO: Remove hardcoding.
            tranches.append(data[j][3] + "_" + str(i+1))
            quantity.append( float(data[j][7+2*i] ) )
            price.append( float(data[j][8+2*i]) )
        j = j+1
        
    return (tranches, price, quantity)

def GenerateMultiOfferData(num_stacks, price_marks, quantity_marks, p_dev = 0, q_dev = 0):
    '''
    Generates price and quantity data fluctuating around certain price
    and quantity 'marks' for a single node case with multiple demand
    scenarios.

    RETURNS:    price       - unsorted nested lists of prices for each demand
                quantity    - unsorted nested lists of quantites for each demand
    '''
    price = []
    quantity = []
    tranches = []

    for i in range(num_stacks):
        price.append([])
        quantity.append([])
        tranches.append([])
        (tranches[i], price[i], quantity[i]) = GenerateOfferData(1, price_marks, quantity_marks, p_dev, q_dev)

    return (tranches, price, quantity)

def GenerateOfferData(num_stacks, price_marks, quantity_marks, p_dev = 0, q_dev = 0):
    '''
    Generates price and quantity data fluctuating around certain
    price and quantity 'marks'.

    RETURNS:    price       - unsorted list of prices
                quantity    - unsorted list of quantities
    '''
    price = []
    quantity = []

    for i in range(num_stacks):
        for j in range(len(price_marks)):
            price.append( round(random.uniform(
                price_marks[j]- p_dev, price_marks[j] + p_dev), 2))
            quantity.append( round(random.uniform(
                quantity_marks[j]- q_dev, quantity_marks[j] + q_dev), 2))
    tranches = range(len(price))
    
    return (tranches, price, quantity)


def GenerateOfferDemands(num_stacks, base = 0, diff = 30, dev = 30):
    '''
    Generates demands and demand probabilities

    RETURNS:    demands     - list of demands
                d_prob      - list of probabilities of each demand occurring
    '''
    demands = []
    for i in range(num_stacks):
        demands.append( base + round(random.uniform(diff*(i+1) - dev, 
            diff*(i+1) + dev), 2))

    # d_prob = GenerateProbabilities(num_stacks)
    d_prob = [1.0/num_stacks]*num_stacks

    return demands, d_prob

            
def GenerateOfferStackPoints(tranches, price, quantity):
    '''
    Generates the points required to plot the offer stack in a
    figure.

    INPUTS:     price       - list of prices
                quantity    - list of quantities
    RETURNS:    p           - sorted list of price points
                q           - sorted list of quantity points
    '''
    #   Sort data
    sort_list = zip(price, quantity)
    list.sort(sort_list)
    (price, quantity) = zip(*sort_list)

    #   Calculate parameterised values
    n = 0
    p = [0, price[n]]
    q = [0, 0]
    for i in range(len(price)-1):
        q.append( q[-1] + quantity[n] )
        q.append( q[-1] )
        n = n + 1
        p.append( p[-1] )
        p.append( price[n] )
    p.append( p[-1] )
    q.append( q[-1] + quantity[n] )

    tranches = range(len(price))

    return (tranches, p, q)

def SplitDataByNode(nodes, tranch, price, quantity, M,
                        single_on = 0):
    '''
    Splits up tranch data by node.

    INPUTS:     nodes       - list of nodes
                tranch      - list of tranches
                price       - dict of prices {TRANCH}
                quantity    - dict of quantities {TRANCH}
                M           - dict mapping tranch to node {TRANCH}
    RETURNS:    p           - sorted list of price points
                q           - sorted list of quantity points
    '''

    #   Split data up by node.
    prices = [[] for i in range(len(nodes))]
    quantities = [[] for i in range(len(nodes))]
    tranches = [[] for i in range(len(nodes))]
    i=0

    if single_on:
        for n in nodes:
            for t in tranch:
                if nodes[0] == n: # For single node case
                    tranches[i].append(t)
                    prices[i].append(price[t])
                    quantities[i].append(quantity[t])
            i = i+1
    else:
        for n in nodes:
            for t in tranch:
                if M[t] == n: # For multi node case
                    tranches[i].append(t)
                    prices[i].append(price[t])
                    quantities[i].append(quantity[t])
            
            i = i+1
    
    # Set last offer to be price max(p), quantity 0 for each node.e
    for i in range(len(nodes)):
        tranches[i].append(t)
        prices[i].append( 2000)
        quantities[i].append(0)

    return (tranches, prices, quantities)

def ParameteriseOfferStack(tranches, price, quantity):
    '''
    Parameterises the prices and quantities in a file in terms of a 
    variable, t, which moves along the set of offer tranches.

    INPUTS:     price       - list of prices
                quantity    - list of quantities
    RETURNS:    price(t)    - sorted list of parameterised price points
                quantity(t) - sorted list of parameterised quantity points
                pq(t)       - sorted list of price * quantity
                t           - sorted list of t points
    '''
    #   Sort data    
    sort_list = zip(price, tranches, quantity)
    list.sort(sort_list)
    (price, tranches, quantity) = zip(*sort_list)
    
    #   Calculate paramaterised values
    n = 0
    pt = [0, price[n]]
    qt = [0, 0]
    pqt = [0, 0]
    tranchid = [0, tranches[n]]
    for i in range(len(price)-1):
        pt.append( pt[-1] )
        qt.append( qt[-1] + quantity[n] )
        pqt.append( qt[-1] * pt[-1] )
        tranchid.append( tranches[n] )

        pt.append( price[n+1] )
        qt.append( qt[-1] )
        pqt.append( qt[-1] * pt[-1] )
        tranchid.append( tranches[n+1] )
        n = n+1
        
    pt.append( price[n] )
    qt.append( qt[-1] + quantity[n] )
    pqt.append(qt[-1] * pt[-1] )
    tranchid.append( tranches[n] )
    return (tranchid, pt, qt, pqt)

def GenerateProbabilities(n):
    ''' 
    Returns a list of n random probabilities which sum to 1.

    INPUTS:     n - number of probabilities
    RETURNS:    p - list of probabilities
    '''
    p = [0] * n

    for i in range(n):
        p[i] = random.random()

    total = sum(p)

    for i in range(n):
        p[i] /= total

    return p

if __name__ == "__main__":
	main()

