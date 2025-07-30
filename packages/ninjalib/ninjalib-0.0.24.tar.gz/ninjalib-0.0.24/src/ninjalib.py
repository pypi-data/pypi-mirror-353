import binascii
import itertools
import math
import statistics
import struct

class ninjalib:
    def __init__(self,data,a=0,b=0,c=0):
        self.data = data
        self.a = a
        self.b = b
        self.c = c

    def cluster(self):
        combos = ninjalib(self.data).combo()
        distances = []
        for i in combos:
            distances.append((abs(i[0]-i[1]),i))
        distances.sort()
        j = None
        clusters = []
        temp_clusters = []
        for i in distances:
            if i[0] != j:
                clusters.append(tuple(temp_clusters))
                temp_clusters = []
                temp_clusters.append(i[1])
            else:
                temp_clusters.append(i[1])
            j = i[0]
        return [i for i in clusters if i]

    def combo(self):
        hits = []
        self.data = list(dict.fromkeys(self.data[:]))
        for i in range(len(self.data)):
            for j in range(len(self.data)):
                hits.append([self.data[i],self.data[j]])
        return hits

    def flatten(self):
        new_data = self.data
        if self.a == 0:
            while True:
                if isinstance(new_data[0],list) or isinstance(new_data[0],tuple):
                    new_data = list(itertools.chain(*new_data))
                else:
                    break
        else:
            for i in range(self.a):
                if isinstance(new_data[0],list) or isinstance(new_data[0],tuple):
                    new_data = list(itertools.chain(*new_data))
        return new_data

    def mean(self):
        return sum(self.data) / len(self.data)
