#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 09:39:25 2020

@author: devalfa
"""
SUS = 100
TOINF = 101
INF = 102
TOQ = 103
Q = 104
TOREC = 105
REC = 106
prob_infects = [0.3, 0.3, 0.4, 0.5, 0.6, 0.6, 0.6, 0.6, 0.7, 0.8, 0.8, 0.9, 0.9, 1]
prob_symptoms = [0.01, 0.11, 0.26, 0.46, 0.86, 0.92, 0.94, 0.95, 0.96, 0.98, 0.99, 0.99, 0.99, 1]
prob_stay_in = [1 for x in range(14)]
import random
import networkx as nx

import matplotlib.pyplot as plt



ref = {}
class node:
    def __init__(self, G, name):
        self.name = name
        self.neighbors = G.neighbors(name)
        self.days = 0
        self.state = SUS
    def changeState(self, state):
        self.state = state
    def transit(self):
        if(self.state==TOINF):
            self.state = INF
        elif(self.state==TOREC):
            self.state = REC
        elif(self.state==TOQ):
            self.state = Q
    def spread(self):
        if(self.state!=INF):
            return
        nb = []
        for neighbor in self.neighbors:
            nd = ref[neighbor]
            if(nd.state!=SUS):
                continue
            else:
                nb.append(nd)
        for nd in nb:
            num = random.uniform(0, 1)
            if(self.days>13):
                self.changeState(TOREC)
                break
            elif(num<prob_infects[self.days]):
                nd.changeState(TOINF)
    def quarantine(self):
        num = random.uniform(0, 1)
        if(self.days>13):
            self.changeState(TOREC)
            return
        delta = prob_stay_in[self.days]
        if(num<delta):
            self.changeState(TOQ)
            self.days = 0
        else:
            self.days+=1
    def recover(self, gamma):
        num = random.uniform(0, 1)
        if(num<gamma or self.days>12):
            self.changeState(TOREC)
        else:
            self.days+=1
            
s = input("Enter name of file: ")                
G = nx.read_edgelist(path = "/home/devalfa/Network/"+s+".txt") 
#G = nx.barabasi_albert_graph(5000,18)         
nodes = G.nodes()            
def reset():
    for nd in nodes:
        ref[nd] = node(G, nd) 

def SIQR(spreaders, gamma, time):
    for nd in spreaders:
        ref[nd].changeState(TOINF)
    s_scale = []
    q_scale = []
    i_scale = []
    r_scale = []
    t=0
    while(t<time):
        t+=1
        for nod in nodes:
            nd = ref[nod]
            if(nd.state==INF):
                nd.spread()
                nd.quarantine()
            elif(nd.state==Q):
                nd.recover(gamma)
        s = 0
        q = 0
        i = 0
        r = 0
        for nod in nodes:
            nd = ref[nod]
            nd.transit()
            if(nd.state==INF):
                i+=1
            elif(nd.state==REC):
                r+=1
            elif(nd.state==SUS):
                s+=1
            else:
                q+=1
        #print(beta*k1*s/(gamma * (s+a+i+r)))      
        s_scale.append(s)
        q_scale.append(q)
        i_scale.append(i)
        r_scale.append(r)
    return s_scale, i_scale, q_scale, r_scale

def Multi_SIQR(n, spreaders, gamma, time):
    fi_scale = [0 for i in range(time)]
    fr_scale = [0 for i in range(time)]
    fq_scale = [0 for i in range(time)]
    fs_scale = [0 for i in range(time)]
    #fu_scale = [0 for i in range(time)]
    for i in range(n):
        print("round", i+1)
        reset()
        s_scale, i_scale, q_scale, r_scale = SIQR(spreaders, gamma, time)
        for j in range(len(i_scale)):
            fi_scale[j]+=i_scale[j]
        for j in range(len(r_scale)):
            fr_scale[j]+=r_scale[j]
        for j in range(len(s_scale)):
            fs_scale[j]+=s_scale[j]
        for j in range(len(q_scale)):
            fq_scale[j]+=q_scale[j]
    for i in range(time):
        fi_scale[i] = fi_scale[i]/n;
        fr_scale[i] = fr_scale[i]/n;
        #fu_scale[i] = fu_scale[i]/n;
        fs_scale[i] = fs_scale[i]/n;
        fq_scale[i] = fq_scale[i]/n;
    return fs_scale, fi_scale, fq_scale, fr_scale

def simulate(spreader_count, gamma, time):
    spreaders = nx.voterank(G, spreader_count)
    s_scale, i_scale, q_scale, r_scale = Multi_SIQR(10, spreaders, gamma, time)
    plt.plot(range(len(r_scale)), r_scale, '-b', label = "Recovered")
    plt.plot(range(len(i_scale)), i_scale, '-r', label = "Infected")
    plt.plot(range(len(q_scale)), q_scale, '-g', label = "Quarantined")
    plt.plot(range(len(s_scale)), s_scale, '-m', label = "Susceptible")
    plt.xlabel('Time')
    plt.ylabel('F(t)')
    plt.legend(loc='best')  
    plt.savefig('/home/devalfa/Network/Corona'+str(gamma)+'_'+s+'_stay_in'+'.png')
    plt.show()

simulate(70, 0.2, 100)