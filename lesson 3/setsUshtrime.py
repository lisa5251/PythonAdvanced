from symdifference import rezultati

my_set = {1,2,3}
my_set.add(7)
print(my_set)

my_set.remove(3)
print(my_set)

my_set.discard(8)
print(my_set)

my_set.clear()
print(my_set)

print(len(my_set))

print("--------------")
my_list = [1,2,2,2,4,6]

print(my_list)

listaUnike = set(my_list)

listaUnike2 = list(listaUnike)
print(listaUnike)
print(listaUnike2)

print("--------------")

user1_interests={"music","movie","travel"}
user2_interests={"movie","reading","cooking"}
rezultati = user1_interests.intersection(user2_interests)

print(rezultati)

users = {"lisa","edeni","ensari"}

personi= "lisa"
print(personi in users)



















