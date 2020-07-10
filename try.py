def save_tracked(names):
    with open('tracking.txt','a') as file:
        for name in names:
            file.write(name+'\n')

with open('tracking.txt','r') as file:
    names = [x.strip() for x in file.readlines()]
    print(name)
