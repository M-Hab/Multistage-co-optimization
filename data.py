#from pulp import *
import offer_stack as offer_stack
import string
import random
import gom_plot as gom_plot

from pprint import pprint

atl = string.uppercase

def main():
    
    # (nodes, arcs, tranches, contracts,
    # price, quantity,
    # demand, gen_cap, contract_quantities,
    # trans_cap, M, N, L, num_loops) = MultiNodeDataMultiDemand()

    (nodes, arcs, tranches, contracts,
        price, quantity,
        demand, generation_capacity, contract_quantities,
        transmission_capacity, M, N, L, num_loops, rho) = GenerateMultiNodeData()

    # gom_plot.plotmultirdc(tranches, price, quantity, demand, nodes, M)


def GenerateMultiNodeData(node_no = 3, arc_det = 1, arc_id = [], tranch_no = 4, 
                            demand_no = 3, demand_base = 400.0, demand_fluc = 20.0,
                            gen_cap = 80.0, gen_fluc = 20.0,
                            price_fluc = 20.0, quantity_fluc = 20.0,
                            price = [], quantity = [], demand = [], generation_capacity = [],
                            capacity = 100.0 ,rng_seed = 0):
    '''
    Function generates random test data for the multi node case 
    for a varying number of nodes and demand cases.
    '''

    random.seed(rng_seed)
    nodes = ["Node "+atl[n] for n in range(node_no)]

    if arc_det == 1:
        arcs = [(i, j) for i in nodes for j in nodes if i < j]
    else:
        arcs = [(i, j) for i in nodes for j in nodes if arc_id[i][j] == 1]

    tranches = ["Gen %s Offer %s" %(n, t+1) for n in nodes for t in range(tranch_no)]

    contracts = ["C" +str(t+1)  for t in range(2)]

    if len(demand) == 0:
        for d in range(demand_no):
        
            node_data = {   # node: demand, generation capacity, etc
                                n : [demand_base + random.randint(-demand_fluc,demand_fluc), 
                                    gen_cap] #+ random.randint(-gen_fluc,gen_fluc)]
                                    for n in nodes
                }
            demand.append([])
            # generation_capacity.append([])
            price.append([])
            quantity.append([])

            # (demand[d], generation_capacity[d]) = splitDict(node_data)
            (demand[d], generation_capacity) = splitDict(node_data)

            tranch_data = { # tranches: price, quantity, etc
                        tranches[i] : [price_fluc * (i % tranch_no ) + random.randint(1,price_fluc), 
                            quantity_fluc + random.randint(-quantity_fluc/2.0,quantity_fluc/2.0)] if i != (len(tranches) -1) else
                            [200.0, demand_base]
                            for i in range(len(tranches))
                }
            (price[d], quantity[d]) = splitDict(tranch_data)


    # else:
    #     node_data = {   # node: demand, generation capacity, etc
    #                         n : [demand + random.randomint(-demand_fluc,demand_fluc), 
    #                             gen_cap + random.randomint(-gen_fluc,gen_fluc)]
    #                             for n in nodes
    #         }
    #     tranch_data = { # tranches: demand, generation capacity, etc
    #                             t : [price[d][j], quantity[d][j]
    #                                 for i in range(tranch_no)
    #         }
    
    transmission_capacity = { # arcs: capacity, etc
                                a   : capacity
                                for a in arcs
        }
    
    contract_quantities = [0]*len(contracts)

    contract_data = { # node    : contracted quantity
            contracts[i]   : contract_quantities[i] 
            for i in range(len(contract_quantities))
        }

    contract_quantity = contract_data

    demand_probabilities = [1.0/len(demand) for i in range(len(demand))]

    M = {   # nodes, tranches, IF node is in tranch
            t : n for t in tranches for n in nodes if n in t
        }

    num_loops = 0

    loop_number = 0

    L = { # ((i,j), loop number) : reactance
        (a, loop_number) : 1.0 if random.random() < 2.0/3.0 else -1.0 for a in arcs 
        }

    N = {
                (nodes[i], contracts[j]) : 1 if i == j
        else    0  for i in range(len(nodes)) for j in range(len(contracts))
        }


    return (nodes, arcs, tranches, contracts,
        price, quantity,
        demand, generation_capacity, contract_quantity,
        transmission_capacity, M, N, L, num_loops, demand_probabilities)



def MultiNodeDataDemand():
    '''
    Hard coded 3 node data.
    '''

    nodes = ["Node A",
             "Node B",
             "Node C"]
    arcs = [("Node A","Node B"),
            ("Node B","Node C"),
            ("Node A","Node C")]
    tranches = ["Gen A Offer 1",
                "Gen A Offer 2",
                "Gen B Offer 1",
                "Gen C Offer 1",
                "Gen C Offer 2"]
    contracts = ["Contract 1",
                 "Contract 2",
                 "Contract 3"]

    node_data = { # node : demand, generation capacity, etc
                ("Node A") : [150.0,100.0],
                ("Node B") : [100.0, 50.0],
                ("Node C") : [150.0,100.0]
            }

    transmission_capacity = {# arc_data = { # arc  : capacity, etc
            ("Node A", "Node B") : 1000.0,
            ("Node B", "Node C") : 1000.0,
            ("Node A", "Node C") : 1000.0,
            }
    
    tranch_data = { # tranch     : price, quantity, etc
                "Gen B Offer 1" : [2.0, 100.0],
                "Gen A Offer 1" : [1.0, 100.0],
                "Gen A Offer 2" : [5.0, 100.0],
                "Gen C Offer 1" : [3.0, 100.0],
                "Gen C Offer 2" : [10.0, 100.0]
                }

    contract_data = { # node    : contracted quantity
            "Contract 1"    : 0,
            "Contract 2"    : 0,
            "Contract 3"    : 0
            }

    (demand, generation_capacity) = splitDict(node_data)
    #capacity = splitDict(arc_data)
    (price, quantity) = splitDict(tranch_data)
    contract_quantities = contract_data
    
    M = {("Node A", tranches[0]) : 1,
         ("Node A", tranches[1]) : 1,
         ("Node A", tranches[2]) : 0,
         ("Node A", tranches[3]) : 0,
         ("Node A", tranches[4]) : 0,
         ("Node B", tranches[0]) : 0,
         ("Node B", tranches[1]) : 0,
         ("Node B", tranches[2]) : 1,
         ("Node B", tranches[3]) : 0,
         ("Node B", tranches[4]) : 0,
         ("Node C", tranches[0]) : 0,
         ("Node C", tranches[1]) : 0,
         ("Node C", tranches[2]) : 0,
         ("Node C", tranches[3]) : 1,
         ("Node C", tranches[4]) : 1
        }

    num_loops = 1
    L = { # ((i,j), loop number) : reactance
        (("Node A", "Node B"), 0) : 1.0,
        (("Node B", "Node C"), 0) : 1.0,
        (("Node A", "Node C"), 0) : -1.0
        }

    N = {   # Node : Quantity
        ("Node A", contracts[0]) : 1,
        ("Node A", contracts[1]) : 0,
        ("Node A", contracts[2]) : 0,
        ("Node B", contracts[0]) : 0,
        ("Node B", contracts[1]) : 1,
        ("Node B", contracts[2]) : 0,
        ("Node C", contracts[0]) : 0,
        ("Node C", contracts[1]) : 0,
        ("Node C", contracts[2]) : 1
        }

    return (nodes, arcs, tranches, contracts,
            price, quantity,
            demand, generation_capacity, contract_quantities,
            transmission_capacity, M, N, L, num_loops)

def MultiNodeDataMultiDemand():
    '''
    Hard coded 3 node data.
    '''

    nodes = ["Node A",
             "Node B",
             "Node C"]
    arcs = [("Node A","Node B"),
            ("Node B","Node C"),
            ("Node A","Node C")]
    tranches = ["Gen A Offer 1",
                "Gen A Offer 2",
                "Gen B Offer 1",
                "Gen C Offer 1",
                "Gen C Offer 2"]
    contracts = ["Contract 1",
                 "Contract 2",
                 "Contract 3"]

    node_data_1 = { # node : demand, generation capacity, etc
                ("Node A") : [150.0,100.0],
                ("Node B") : [100.0, 50.0],
                ("Node C") : [150.0,100.0]
            }

    node_data_2 = { # node : demand, generation capacity, etc
                ("Node A") : [120.0,100.0],
                ("Node B") : [100.0, 50.0],
                ("Node C") : [120.0,100.0]
            }

    transmission_capacity = {# arc_data = { # arc  : capacity, etc
            ("Node A", "Node B") : 1000.0,
            ("Node B", "Node C") : 1000.0,
            ("Node A", "Node C") : 1000.0,
            }
    
    tranch_data_1 = { # tranch     : price, quantity, etc
                "Gen B Offer 1" : [2.0, 100.0],
                "Gen A Offer 1" : [1.0, 100.0],
                "Gen A Offer 2" : [5.0, 100.0],
                "Gen C Offer 1" : [3.0, 100.0],
                "Gen C Offer 2" : [10.0, 100.0]
                }

    tranch_data_2 = { # tranch     : price, quantity, etc
                "Gen B Offer 1" : [1.5, 100.0],
                "Gen A Offer 1" : [0.5, 100.0],
                "Gen A Offer 2" : [4.5, 100.0],
                "Gen C Offer 1" : [2.5, 100.0],
                "Gen C Offer 2" : [12.5, 100.0]
                }

    contract_data = { # node    : contracted quantity
            "Contract 1"    : 0,
            "Contract 2"    : 0,
            "Contract 3"    : 0
            }

    demand_probabilities = [
            0.5,
            0.5]

    
    (demand_1, generation_capacity) = splitDict(node_data_1)
    (demand_2, generation_capacity) = splitDict(node_data_1)    
    #capacity = splitDict(arc_data)
    (price_1, quantity_1) = splitDict(tranch_data_1)
    (price_2, quantity_2) = splitDict(tranch_data_2)

    demand = [demand_1, demand_2]

    price = [price_1, price_2]
    quantity = [quantity_1, quantity_2]

    contract_quantities = contract_data
    
    M = {("Node A", tranches[0]) : 1,
         ("Node A", tranches[1]) : 1,
         ("Node A", tranches[2]) : 0,
         ("Node A", tranches[3]) : 0,
         ("Node A", tranches[4]) : 0,
         ("Node B", tranches[0]) : 0,
         ("Node B", tranches[1]) : 0,
         ("Node B", tranches[2]) : 1,
         ("Node B", tranches[3]) : 0,
         ("Node B", tranches[4]) : 0,
         ("Node C", tranches[0]) : 0,
         ("Node C", tranches[1]) : 0,
         ("Node C", tranches[2]) : 0,
         ("Node C", tranches[3]) : 1,
         ("Node C", tranches[4]) : 1
        }



    num_loops = 1
    L = { # ((i,j), loop number) : reactance
        (("Node A", "Node B"), 0) : 1.0,
        (("Node B", "Node C"), 0) : 1.0,
        (("Node A", "Node C"), 0) : -1.0
        }

    N = {   # Node : Quantity
        ("Node A", contracts[0]) : 1,
        ("Node A", contracts[1]) : 0,
        ("Node A", contracts[2]) : 0,
        ("Node B", contracts[0]) : 0,
        ("Node B", contracts[1]) : 1,
        ("Node B", contracts[2]) : 0,
        ("Node C", contracts[0]) : 0,
        ("Node C", contracts[1]) : 0,
        ("Node C", contracts[2]) : 1
        }

    return (nodes, arcs, tranches, contracts,
            price, quantity, demand_probabilities,
            demand, generation_capacity, contract_quantities,
            transmission_capacity, M, N, L, num_loops)


def MultiNodeDataMultiDemand2():
    '''
    Hard coded 3 node data.
    '''

    nodes = ["Node A",
             "Node B",
             "Node C"]
    arcs = [("Node A","Node B"),
            ("Node B","Node C"),
            ("Node A","Node C")]

    tranches = ["Gen A Offer 1",
                "Gen A Offer 2",
                "Gen A Offer 3",
                "Gen A Offer 4",
                "Gen B Offer 1",
                "Gen B Offer 2",
                "Gen B Offer 3",
                "Gen C Offer 1",
                "Gen C Offer 2",
                "Gen C Offer 3",
                "Gen C Offer 4"
                ]


    contracts = ["Contract 1",
                 "Contract 2",
                 "Contract 3"]

    node_data_1 = { # node : demand, generation capacity, etc
                ("Node A") : [150.0,100.0],
                ("Node B") : [100.0, 50.0],
                ("Node C") : [150.0,100.0]
            }

    node_data_2 = { # node : demand, generation capacity, etc
                ("Node A") : [120.0,100.0],
                ("Node B") : [100.0, 50.0],
                ("Node C") : [120.0,100.0]
            }

    node_data_3 = { # node : demand, generation capacity, etc
                ("Node A") : [100.0,100.0],
                ("Node B") : [120.0, 50.0],
                ("Node C") : [100.0,100.0]
            }

    node_data_4 = { # node : demand, generation capacity, etc
                ("Node A") : [160.0,100.0],
                ("Node B") : [180.0, 50.0],
                ("Node C") : [160.0,100.0]
            }

    node_data_5 = { # node : demand, generation capacity, etc
                ("Node A") : [200.0,100.0],
                ("Node B") : [150.0, 50.0],
                ("Node C") : [200.0,100.0]
            }

    node_data_6 = { # node : demand, generation capacity, etc
                ("Node A") : [180.0,100.0],
                ("Node B") : [110.0, 50.0],
                ("Node C") : [180.0,100.0]
            }

    transmission_capacity = {# arc_data = { # arc  : capacity, etc
            ("Node A", "Node B") : 1000.0,
            ("Node B", "Node C") : 1000.0,
            ("Node A", "Node C") : 1000.0,
            }
    
    tranch_data_1 = { # tranch     : price, quantity, etc
                "Gen B Offer 1" : [1.0, 100.0],
                "Gen B Offer 2" : [3.0, 100.0],
                "Gen B Offer 3" : [6.0, 100.0],
                "Gen A Offer 3" : [7.0, 100.0],
                "Gen A Offer 1" : [1.0, 100.0],
                "Gen A Offer 2" : [5.0, 100.0],
                "Gen A Offer 4" : [5000, 5.0],
                "Gen C Offer 1" : [3.0, 100.0],
                "Gen C Offer 2" : [10.0, 100.0],
                "Gen C Offer 3" : [13.0, 100.0],
                "Gen C Offer 4" : [15.0, 100.0],
                }

    tranch_data_2 = { # tranch     : price, quantity, etc
                "Gen B Offer 1" : [2.0, 100.0],
                "Gen B Offer 2" : [4.0, 100.0],
                "Gen B Offer 3" : [7.0, 100.0],
                "Gen A Offer 3" : [6.0, 100.0],
                "Gen A Offer 1" : [1.0, 100.0],
                "Gen A Offer 2" : [4.0, 100.0],
                "Gen A Offer 4" : [5000, 5.0],
                "Gen C Offer 1" : [5.0, 100.0],
                "Gen C Offer 2" : [12.0, 100.0],
                "Gen C Offer 3" : [13.0, 100.0],
                "Gen C Offer 4" : [14.0, 100.0],
                }
    tranch_data_3 = { # tranch     : price, quantity, etc
                "Gen B Offer 1" : [1.5, 100.0],
                "Gen B Offer 2" : [3.2, 100.0],
                "Gen B Offer 3" : [6.7, 100.0],
                "Gen A Offer 3" : [9.0, 100.0],
                "Gen A Offer 1" : [0.80, 100.0],
                "Gen A Offer 2" : [7.0, 100.0],
                "Gen A Offer 4" : [5000, 5.0],
                "Gen C Offer 1" : [4.0, 100.0],
                "Gen C Offer 2" : [14.0, 100.0],
                "Gen C Offer 3" : [15.0, 100.0],
                "Gen C Offer 4" : [20.0, 100.0],
                }

    tranch_data_4 = { # tranch     : price, quantity, etc
                "Gen B Offer 1" : [2.5, 100.0],
                "Gen B Offer 2" : [4.5, 100.0],
                "Gen B Offer 3" : [8.5, 100.0],
                "Gen A Offer 3" : [6.5, 100.0],
                "Gen A Offer 1" : [2.0, 100.0],
                "Gen A Offer 2" : [4.0, 100.0],
                "Gen A Offer 4" : [5000, 5.0],
                "Gen C Offer 1" : [3.0, 100.0],
                "Gen C Offer 2" : [8.0, 100.0],
                "Gen C Offer 3" : [12.0, 100.0],
                "Gen C Offer 4" : [16.0, 100.0],
                }
    tranch_data_5 = { # tranch     : price, quantity, etc
                "Gen B Offer 1" : [3.0, 100.0],
                "Gen B Offer 2" : [4.0, 100.0],
                "Gen B Offer 3" : [5.0, 100.0],
                "Gen A Offer 3" : [5.0, 100.0],
                "Gen A Offer 1" : [1.2, 100.0],
                "Gen A Offer 2" : [3.0, 100.0],
                "Gen A Offer 4" : [5000, 5.0],
                "Gen C Offer 1" : [2.0, 100.0],
                "Gen C Offer 2" : [8.0, 100.0],
                "Gen C Offer 3" : [13.0, 100.0],
                "Gen C Offer 4" : [15.5, 100.0],
                }

    tranch_data_6 = { # tranch     : price, quantity, etc
                "Gen B Offer 1" : [3.3, 100.0],
                "Gen B Offer 2" : [6.7, 100.0],
                "Gen B Offer 3" : [8.0, 100.0],
                "Gen A Offer 3" : [4.2, 100.0],
                "Gen A Offer 1" : [2.0, 100.0],
                "Gen A Offer 2" : [3.0, 100.0],
                "Gen A Offer 4" : [5000, 5.0],
                "Gen C Offer 1" : [2.0, 100.0],
                "Gen C Offer 2" : [3.0, 100.0],
                "Gen C Offer 3" : [6.0, 100.0],
                "Gen C Offer 4" : [9.0, 100.0],
                }
    contract_data = { # node    : contracted quantity
            "Contract 1"    : 0,
            "Contract 2"    : 0,
            "Contract 3"    : 0
            }

    demand_probabilities = [
            0.5,
            0.5]

    
    (demand_1, generation_capacity) = splitDict(node_data_1)
    (demand_2, generation_capacity) = splitDict(node_data_2)
    (demand_3, generation_capacity) = splitDict(node_data_3)
    (demand_4, generation_capacity) = splitDict(node_data_4)  
    (demand_5, generation_capacity) = splitDict(node_data_5)
    (demand_6, generation_capacity) = splitDict(node_data_6)  
    #capacity = splitDict(arc_data)
    (price_1, quantity_1) = splitDict(tranch_data_1)
    (price_2, quantity_2) = splitDict(tranch_data_2)
    (price_3, quantity_3) = splitDict(tranch_data_3)
    (price_4, quantity_4) = splitDict(tranch_data_4)
    (price_5, quantity_5) = splitDict(tranch_data_5)
    (price_6, quantity_6) = splitDict(tranch_data_6)

    demand = [demand_1, demand_2, demand_3,demand_4,demand_5,demand_6]

    price = [price_1, price_2,price_3,price_4,price_5,price_6]
    quantity = [quantity_1, quantity_2,quantity_3,quantity_4,quantity_5,quantity_6]

    contract_quantities = contract_data
    
    # M = {"Node A" : tranches[0],
    #      "Node A": tranches[1],
    #      "Node A": tranches[2],
    #      "Node A": tranches[3],
    #      "Node B": tranches[4],
    #      "Node B": tranches[5],
    #      "Node B": tranches[6],
    #      "Node C": tranches[7],
    #      "Node C": tranches[8],
    #      "Node C": tranches[9],
    #      "Node C": tranches[10]
    #     }

    M = {tranches[0] :"Node A",
         tranches[1] :"Node A",
         tranches[2] :"Node A",
         tranches[3] :"Node A",
         tranches[4] :"Node B",
         tranches[5] :"Node B",
         tranches[6] :"Node B",
         tranches[7] :"Node C",
         tranches[8] :"Node C",
         tranches[9] :"Node C",
         tranches[10] :"Node C"
    }

    num_loops = 1
    L = { # ((i,j), loop number) : reactance
        (("Node A", "Node B"), 0) : 1.0,
        (("Node B", "Node C"), 0) : 1.0,
        (("Node A", "Node C"), 0) : -1.0
        }

    N = {   # Node : Quantity
        ("Node A", contracts[0]) : 1,
        ("Node A", contracts[1]) : 0,
        ("Node A", contracts[2]) : 0,
        ("Node B", contracts[0]) : 0,
        ("Node B", contracts[1]) : 1,
        ("Node B", contracts[2]) : 0,
        ("Node C", contracts[0]) : 0,
        ("Node C", contracts[1]) : 0,
        ("Node C", contracts[2]) : 1
        }

    return (nodes, arcs, tranches, contracts,
            price, quantity, demand_probabilities,
            demand, generation_capacity, contract_quantities,
            transmission_capacity, M, N, L, num_loops)

def MultiNodeDataMultiDemand3():
    '''
    Hard coded 3 node data.
    '''

    nodes = ["Node A",
             "Node B",
             "Node C"]
    arcs = [("Node A","Node B"),
            ("Node B","Node C"),
            ("Node A","Node C")]

    tranches = ["Gen A Offer 1",
                "Gen A Offer 2",
                "Gen A Offer 3",
                "Gen A Offer 4",
                "Gen B Offer 1",
                "Gen B Offer 2",
                "Gen B Offer 3",
                "Gen C Offer 1",
                "Gen C Offer 2",
                "Gen C Offer 3",
                "Gen C Offer 4"
                ]


    contracts = ["Contract 1",
                 "Contract 2",
                 "Contract 3"]

    node_data_1 = { # node : demand, generation capacity, etc
                ("Node A") : [90.0,150.0],
                ("Node B") : [40.0, 70.0],
                ("Node C") : [90.0,150.0]
            }

    node_data_2 = { # node : demand, generation capacity, etc
                ("Node A") : [200.0,150.0],
                ("Node B") : [140.0, 70.0],
                ("Node C") : [200.0,150.0]
            }

    transmission_capacity = {# arc_data = { # arc  : capacity, etc
            ("Node A", "Node B") : 1000.0,
            ("Node B", "Node C") : 1000.0,
            ("Node A", "Node C") : 1000.0,
            }
    
    tranch_data_1 = { # tranch     : price, quantity, etc
                "Gen B Offer 1" : [1.0, 100.0],
                "Gen B Offer 2" : [3.0, 100.0],
                "Gen B Offer 3" : [500.0, 30.0],
                "Gen A Offer 3" : [7.0, 100.0],
                "Gen A Offer 1" : [1.0, 100.0],
                "Gen A Offer 2" : [5.0, 100.0],
                "Gen A Offer 4" : [500, 100.0],
                "Gen C Offer 1" : [3.0, 100.0],
                "Gen C Offer 2" : [10.0, 100.0],
                "Gen C Offer 3" : [13.0, 100.0],
                "Gen C Offer 4" : [500.0, 100.0],
                }

    tranch_data_2 = { # tranch     : price, quantity, etc
                "Gen B Offer 1" : [2.0, 100.0],
                "Gen B Offer 2" : [4.0, 100.0],
                "Gen B Offer 3" : [500.0, 300.0],
                "Gen A Offer 3" : [6.0, 100.0],
                "Gen A Offer 1" : [1.0, 100.0],
                "Gen A Offer 2" : [4.0, 100.0],
                "Gen A Offer 4" : [500, 300.0],
                "Gen C Offer 1" : [5.0, 100.0],
                "Gen C Offer 2" : [12.0, 100.0],
                "Gen C Offer 3" : [13.0, 100.0],
                "Gen C Offer 4" : [500.0, 300.0],
                }

    contract_data = { # node    : contracted quantity
            "Contract 1"    : 0,
            "Contract 2"    : 0,
            "Contract 3"    : 0
            }

    demand_probabilities = [
            0.5,
            0.5]

    
    (demand_1, generation_capacity) = splitDict(node_data_1)
    (demand_2, generation_capacity) = splitDict(node_data_2)

    #capacity = splitDict(arc_data)
    (price_1, quantity_1) = splitDict(tranch_data_1)
    (price_2, quantity_2) = splitDict(tranch_data_2)


    demand = [demand_1, demand_2]

    price = [price_1, price_2]
    quantity = [quantity_1, quantity_2]

    contract_quantities = contract_data
    
    # M = {"Node A" : tranches[0],
    #      "Node A": tranches[1],
    #      "Node A": tranches[2],
    #      "Node A": tranches[3],
    #      "Node B": tranches[4],
    #      "Node B": tranches[5],
    #      "Node B": tranches[6],
    #      "Node C": tranches[7],
    #      "Node C": tranches[8],
    #      "Node C": tranches[9],
    #      "Node C": tranches[10]
    #     }

    M = {tranches[0] :"Node A",
         tranches[1] :"Node A",
         tranches[2] :"Node A",
         tranches[3] :"Node A",
         tranches[4] :"Node B",
         tranches[5] :"Node B",
         tranches[6] :"Node B",
         tranches[7] :"Node C",
         tranches[8] :"Node C",
         tranches[9] :"Node C",
         tranches[10] :"Node C"
    }

    num_loops = 1
    L = { # ((i,j), loop number) : reactance
        (("Node A", "Node B"), 0) : 1.0,
        (("Node B", "Node C"), 0) : 1.0,
        (("Node A", "Node C"), 0) : -1.0
        }

    N = {   # Node : Quantity
        ("Node A", contracts[0]) : 1,
        ("Node A", contracts[1]) : 0,
        ("Node A", contracts[2]) : 0,
        ("Node B", contracts[0]) : 0,
        ("Node B", contracts[1]) : 1,
        ("Node B", contracts[2]) : 0,
        ("Node C", contracts[0]) : 0,
        ("Node C", contracts[1]) : 0,
        ("Node C", contracts[2]) : 1
        }

    return (nodes, arcs, tranches, contracts,
            price, quantity, demand_probabilities,
            demand, generation_capacity, contract_quantities,
            transmission_capacity, M, N, L, num_loops)

def MultiNodeData3():
    '''
    Hard coded 2 node data, used for testing cost functions and contracts.
    DELETE LATER.
    '''
    nodes = ["Node A",
             "Node B"]
    arcs = [("Node A","Node B")]

    test = 1
    if test:
        tranches = ["Gen A Offer 1",
                "Gen A Offer 2",
                "Gen A Offer 3",
                "Gen B Offer 1",
                "Gen B Offer 2",
                "Gen B Offer 3",
                "Gen C Offer 1",
                "Gen C Offer 2",
                "Gen D Offer 1",
                "Gen D Offer 2"]
    else:
        tranches = ["Gen A Offer 1",
                "Gen A Offer 2",
                "Gen B Offer 1",
                "Gen B Offer 2"]
    
    contracts = ["Contract 1",
                 "Contract 2",
                 "Contract 3"]

    node_data = { # node : demand, generation capacity, etc
                ("Node A") : [250.0, 200.0],
                ("Node B") : [250.0, 200.0]
            }

    transmission_capacity = {# arc_data = { # arc  : capacity, reactance, etc
            ("Node A", "Node B") : 1000.0
            }

    if test:
        tranch_data = { # tranch     : price, quantity, etc
                "Gen A Offer 1" : [1.0, 150.0],
                "Gen A Offer 2" : [10.0, 50.0],
                "Gen A Offer 3" : [50.0, 50.0],
                "Gen B Offer 1" : [2.0, 100.0],
                "Gen B Offer 2" : [10.0, 50.0],
                "Gen B Offer 3" : [60.0, 50.0],
                "Gen C Offer 1" : [0.0, 50.0],
                "Gen C Offer 2" : [20.0, 100.0],
                "Gen D Offer 1" : [1.0, 100.0],
                "Gen D Offer 2" : [30.0, 50.0]
                }
    else:
        tranch_data = { # tranch     : price, quantity, etc
                "Gen A Offer 1" : [1.0, 200.0],
                "Gen A Offer 2" : [2.0, 200.0],
                "Gen B Offer 1" : [3.0, 200.0],
                "Gen B Offer 2" : [4.0, 200.0]
                }
    
    contract_data = { # node    : contracted quantity
        "Contract 1"    : 0.0,
        "Contract 2"    : 50.0,
        "Contract 3"    : 50.0
        }

    (demand, generation_capacity) = splitDict(node_data)
    #capacity = splitDict(arc_data)
    (price, quantity) = splitDict(tranch_data)
    contract_quantities = contract_data

    if test:
        M = {("Node A", tranches[0]) : 1,
         ("Node A", tranches[1]) : 1,
         ("Node A", tranches[2]) : 1,
         ("Node A", tranches[3]) : 0,
         ("Node A", tranches[4]) : 0,
         ("Node A", tranches[5]) : 0,
         ("Node A", tranches[6]) : 1,
         ("Node A", tranches[7]) : 1,
         ("Node A", tranches[8]) : 0,
         ("Node A", tranches[9]) : 0,
         ("Node B", tranches[0]) : 0,
         ("Node B", tranches[1]) : 0,
         ("Node B", tranches[2]) : 0,
         ("Node B", tranches[3]) : 1,
         ("Node B", tranches[4]) : 1,
         ("Node B", tranches[5]) : 1,
         ("Node B", tranches[6]) : 0,
         ("Node B", tranches[7]) : 0,
         ("Node B", tranches[8]) : 1,
         ("Node B", tranches[9]) : 1
         }
    else:
        M = {("Node A", tranches[0]) : 1,
         ("Node A", tranches[1]) : 1,
         ("Node A", tranches[2]) : 0,
         ("Node A", tranches[3]) : 0,
         ("Node B", tranches[0]) : 0,
         ("Node B", tranches[1]) : 0,
         ("Node B", tranches[2]) : 1,
         ("Node B", tranches[3]) : 1
         }

    num_loops = 0
    L = { # ((i,j), loop number) : reactance
        
        }

    N = {   # Node : Quantity
        ("Node A", contracts[0]) : 1,
        ("Node A", contracts[1]) : 1,
        ("Node A", contracts[2]) : 0,
        ("Node B", contracts[0]) : 0,
        ("Node B", contracts[1]) : 0,
        ("Node B", contracts[2]) : 1
        }

    return (nodes, arcs, tranches, contracts,
            price, quantity,
            demand, generation_capacity, contract_quantities,
            transmission_capacity, M, N, L, num_loops)
    


def RandomNetworkData(num_stacks, num_contracts):
    '''
    3 Node set-up, variable offers at each node.
    '''
    
    nodes = ["NodeA",
             "NodeB",
             "NodeC"]
            
    arcs = [("NodeA","NodeB"),
            ("NodeB","NodeC"),
            ("NodeA","NodeC")]

    node_data = { # node : demand, generation capacity, etc
            ("NodeA") : [1000.0,800.0],
            ("NodeB") : [1000.0,800.0],
            ("NodeC") : [1000.0,800.0]
            }

    trans_cap = {# arc_data = { # arc  : capacity, reactance, etc
            ("NodeA", "NodeB") : 500.0,
            ("NodeB", "NodeC") : 500.0,
            ("NodeA", "NodeC") : 500.0
            }
    
    tranch_data = offer_stack.CreateMultipleTranchData(nodes, num_stacks)
    tranches = tranch_data.keys()

    contract_data = offer_stack.CreateMultipleContractData(nodes, num_contracts)
    contracts = contract_data.keys()

    (demand, gen_cap) = splitDict(node_data)
    (price, quantity, tranch_nodes) = splitDict(tranch_data)
    (contract_quantities, contract_nodes) = splitDict(contract_data)

    # M = {}
    # for i in nodes:
    #     for j in tranches:
    #         M[(i,j)] = 0
    # for i in tranches:
    #     M[(tranch_nodes[i], i)] = 1
    M = tranch_nodes

    # N = {}
    # for i in nodes:
    #     for j in contracts:
    #         N[(i,j)] = 0
    # for i in contracts:
    #     N[(contract_nodes[i], i)] = 1
    N = contract_nodes

    num_loops = 1
    L = { # ((i,j), loop number) : reactance
        (("NodeA", "NodeB"), 0) : 1.0,
        (("NodeB", "NodeC"), 0) : 1.0,
        (("NodeA", "NodeC"), 0) : -1.0
        }

    return (nodes, arcs, tranches, contracts,
            price, quantity,
            demand, gen_cap, contract_quantities,
            trans_cap, M, N, L, num_loops)


def MultiNodeData():
    '''
    Hard coded 3 node data.
    '''

    nodes = ["Node A",
             "Node B",
             "Node C"]
    arcs = [("Node A","Node B"),
            ("Node B","Node C"),
            ("Node A","Node C")]
    tranches = ["Gen A Offer 1",
                "Gen A Offer 2",
                "Gen B Offer 1",
                "Gen C Offer 1",
                "Gen C Offer 2"]
    contracts = ["Contract 1",
                 "Contract 2",
                 "Contract 3"]

    node_data = { # node : demand, generation capacity, etc
                ("Node A") : [150.0,100.0],
                ("Node B") : [100.0, 50.0],
                ("Node C") : [150.0,100.0]
            }

    transmission_capacity = {# arc_data = { # arc  : capacity, etc
            ("Node A", "Node B") : 1000.0,
            ("Node B", "Node C") : 1000.0,
            ("Node A", "Node C") : 1000.0,
            }
    
    tranch_data = { # tranch     : price, quantity, etc
                "Gen B Offer 1" : [2.0, 100.0],
                "Gen A Offer 1" : [1.0, 100.0],
                "Gen A Offer 2" : [5.0, 100.0],
                "Gen C Offer 1" : [3.0, 100.0],
                "Gen C Offer 2" : [10.0, 100.0]
                }

    contract_data = { # node    : contracted quantity
            "Contract 1"    : 0,
            "Contract 2"    : 0,
            "Contract 3"    : 0
            }

    (demand, generation_capacity) = splitDict(node_data)
    #capacity = splitDict(arc_data)
    (price, quantity) = splitDict(tranch_data)
    contract_quantities = contract_data
    
    M = {("Node A", tranches[0]) : 1,
         ("Node A", tranches[1]) : 1,
         ("Node A", tranches[2]) : 0,
         ("Node A", tranches[3]) : 0,
         ("Node A", tranches[4]) : 0,
         ("Node B", tranches[0]) : 0,
         ("Node B", tranches[1]) : 0,
         ("Node B", tranches[2]) : 1,
         ("Node B", tranches[3]) : 0,
         ("Node B", tranches[4]) : 0,
         ("Node C", tranches[0]) : 0,
         ("Node C", tranches[1]) : 0,
         ("Node C", tranches[2]) : 0,
         ("Node C", tranches[3]) : 1,
         ("Node C", tranches[4]) : 1
        }

    num_loops = 1
    L = { # ((i,j), loop number) : reactance
        (("Node A", "Node B"), 0) : 1.0,
        (("Node B", "Node C"), 0) : 1.0,
        (("Node A", "Node C"), 0) : -1.0
        }

    N = {   # Node : Quantity
        ("Node A", contracts[0]) : 1,
        ("Node A", contracts[1]) : 0,
        ("Node A", contracts[2]) : 0,
        ("Node B", contracts[0]) : 0,
        ("Node B", contracts[1]) : 1,
        ("Node B", contracts[2]) : 0,
        ("Node C", contracts[0]) : 0,
        ("Node C", contracts[1]) : 0,
        ("Node C", contracts[2]) : 1
        }

    return (nodes, arcs, tranches, contracts,
            price, quantity,
            demand, generation_capacity, contract_quantities,
            transmission_capacity, M, N, L, num_loops)

def MultiNodeDataTest():
    '''
    Hard coded 3 node data. Used to add solution of bilevel problem
    to a the data set, to be solved using just the dispatch model to
    verify results.
    DELETE LATER
    '''

    nodes = ["Node A",
             "Node B",
             "Node C"]
    arcs = [("Node A","Node B"),
            ("Node B","Node C"),
            ("Node A","Node C")]
    tranches = ["Gen A Offer 1",
                "Gen A Offer 2",
                "Gen B Offer 1",
                "Gen C Offer 1",
                "Gen C Offer 2",
                "Strategic Generation A",
                "Strategic Generation B",
                "Strategic Generation C"
                ]
    contracts = ["Contract 1",
                 "Contract 2",
                 "Contract 3"]

    node_data = { # node : demand, generation capacity, etc
                ("Node A") : [150.0,100.0],
                ("Node B") : [100.0, 50.0],
                ("Node C") : [150.0,100.0]
            }

    transmission_capacity = {# arc_data = { # arc  : capacity, etc
            ("Node A", "Node B") : 1000.0,
            ("Node B", "Node C") : 1000.0,
            ("Node A", "Node C") : 1000.0,
            }
    
    tranch_data = { # tranch     : price, quantity, etc
                "Gen B Offer 1" : [2.0, 100.0],
                "Gen A Offer 1" : [1.0, 100.0],
                "Gen A Offer 2" : [5.0, 100.0],
                "Gen C Offer 1" : [3.0, 100.0],
                "Gen C Offer 2" : [10.0, 100.0],
                "Strategic Generation A" : [0.0, 100.0],
                "Strategic Generation B" : [0.0, 50.0],
                "Strategic Generation C" : [0.0, 41.66666666]
                }

    contract_data = { # node    : contracted quantity
            "Contract 1"    : 0,
            "Contract 2"    : 0,
            "Contract 3"    : 0
            }

    (demand, generation_capacity) = splitDict(node_data)
    #capacity = splitDict(arc_data)
    (price, quantity) = splitDict(tranch_data)
    contract_quantities = contract_data
    
    M = {("Node A", tranches[0]) : 1,
         ("Node A", tranches[1]) : 1,
         ("Node A", tranches[2]) : 0,
         ("Node A", tranches[3]) : 0,
         ("Node A", tranches[4]) : 0,
         ("Node A", tranches[5]) : 1,
         ("Node A", tranches[6]) : 0,
         ("Node A", tranches[7]) : 0,
         ("Node B", tranches[0]) : 0,
         ("Node B", tranches[1]) : 0,
         ("Node B", tranches[2]) : 1,
         ("Node B", tranches[3]) : 0,
         ("Node B", tranches[4]) : 0,
         ("Node B", tranches[5]) : 0,
         ("Node B", tranches[6]) : 1,
         ("Node B", tranches[7]) : 0,
         ("Node C", tranches[0]) : 0,
         ("Node C", tranches[1]) : 0,
         ("Node C", tranches[2]) : 0,
         ("Node C", tranches[3]) : 1,
         ("Node C", tranches[4]) : 1,
         ("Node C", tranches[5]) : 0,
         ("Node C", tranches[6]) : 0,
         ("Node C", tranches[7]) : 1
        }

    num_loops = 1
    L = { # ((i,j), loop number) : reactance
        (("Node A", "Node B"), 0) : 1.0,
        (("Node B", "Node C"), 0) : 1.0,
        (("Node A", "Node C"), 0) : -1.0
        }

    N = {   # Node : Quantity
        ("Node A", contracts[0]) : 1,
        ("Node A", contracts[1]) : 0,
        ("Node A", contracts[2]) : 0,
        ("Node B", contracts[0]) : 0,
        ("Node B", contracts[1]) : 1,
        ("Node B", contracts[2]) : 0,
        ("Node C", contracts[0]) : 0,
        ("Node C", contracts[1]) : 0,
        ("Node C", contracts[2]) : 1
        }

    return (nodes, arcs, tranches, contracts,
            price, quantity,
            demand, generation_capacity, contract_quantities,
            transmission_capacity, M, N, L, num_loops)


if __name__ == "__main__":
	main()

