
dict = {"Gabe": 2, "Jacob": 5, "Jack": 4, "Tanner": 1}
players = []

dict = {key: value for key, value in sorted(dict.items(), key=lambda item: item[1])}

for k in dict.keys():
    players.append(k)
print(players)
