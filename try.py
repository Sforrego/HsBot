text = """
ijsberg2
IronRok
Iron Rar
DeadLinaty
CluelessProd
NoobForSoup
maxitaxi777
J osho
Kwartje
83 openkey
Iron Natedwg
Polybos
Und3r0ath
i r 0 n 3 d
Spooned Soul
No GE Canvey
Ciaran Sor
Toad Event
chrizzoz95
SalmonLemone
R a df o r d
Rkylem
IM Knight
TheBranFlake
Its Ruhspect
Superhcfire
HCb
fdsd
"""
list = text.replace(" ", "_").split(" ")
for i in range(len(list)):
    list[i] = list[i].lower()

print(" ".join(list))
