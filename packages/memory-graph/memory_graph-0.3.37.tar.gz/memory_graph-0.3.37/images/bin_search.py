import memory_graph as mg

class View:

    def __init__(self, lst, begin, end):
        self.lst = lst
        self.begin = begin
        self.end = end

    def __getitem__(self, index):
        return self.lst[index]
        
    def get_mid(self):
        return (self.begin + self.end) // 2

def bin_search(view, value):
    mid = view.get_mid()
    mid_value = view[mid]
    if value < mid_value:
        return bin_search(View(view.lst, view.begin, mid), value)
    elif value > mid_value:
        return bin_search(View(view.lst, mid, view.end), value)
    else:
        return mid


n = 15
data = [i for i in range(n)]
value = n//3
index = bin_search(View(data, 0, len(data)), value)
print(f'{index=}')