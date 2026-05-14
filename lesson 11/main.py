import os
file = open("example.txt","r")

file.close()

with open("example.txt","r")as file:
    content = file.read()
    print(content)

with open("example.txt","w")as file:
    file.write("hello from main")

lista = ["Hello world!\n", "Welcome to python!\n"]

with open("example.txt","w")as file:
    file.writelines(lista)

if os.path.exists("example.txt"):
    print("file ekziston")

if os.path.exists("fds.txt"):
    print("file ekziston")
else:
    print("file fds nuk ekziston")

with open("example.txt","a")as file:
    file.write("hello sfd main")

name="Donjeta"
age=65468

with open("output.txt","w")as file:
    file.write("Name: "+ name + "\n")
    file.write("Age: " + str(age) + "\n")