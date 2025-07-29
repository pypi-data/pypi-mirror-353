def average_mm(m):
    a=len(m)
    if a == 0:
        return 0    
    else:
        j=0
        for i in m:
            i= int(i)
            j= i +j 
        return j/a

