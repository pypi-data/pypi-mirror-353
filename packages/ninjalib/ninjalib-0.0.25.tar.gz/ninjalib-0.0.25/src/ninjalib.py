import itertools

class ninjalib:
    def __init__(self,data,a=0,b=0,c=0):
        self.data = data
        self.a = a
        self.b = b
        self.c = c

    def combo(self):
        hits = []
        self.data = list(dict.fromkeys(self.data[:]))
        self.data.sort()
        for i in range(len(self.data)):
            for j in range(len(self.data)):
                hits.append([self.data[i],self.data[j]])
        return hits

    def diff(self):
        combos = ninjalib(self.data).combo()
        distances = []
        for i in combos:
            if abs(i[0]-i[1]) > 0:
                distances.append((abs(i[0]-i[1]),i))
        distances.sort()
        return distances

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
