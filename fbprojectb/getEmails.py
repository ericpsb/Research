from facepy import GraphAPI
with open("longtermaccesstoken.txt","r") as file:
        a =[]
        for line in file:
            if (line != '\n'):
                access_token=line.split(',')[0]
                try:
                   graph = GraphAPI(access_token)
                   info = graph.get("me?fields=email,name,id")
                   if (info['name'] not in ["Neha Deshmukh","Yihui Fu","Xiong Chu","Eric P. S. Baumer"]):
                          a.append(info)
                except:
                   print "Missed"
f = open("emails.txt","w")
f.write(str([dict(tupleized) for tupleized in set(tuple(item.items()) for item in a)]))
f.close()
