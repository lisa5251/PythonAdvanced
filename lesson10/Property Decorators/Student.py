class Student:

    def __init__(self, name, age):
        self.__name = name
        self.__age = age


   @property
   def name(self):
        return self.__name


   @property
   def age(self):
        return self.__age

   @age.setter
   def age(self, age):
       self.__age=age

   @name.setter
   def age(self, name):
       self.__name=name

studenti = Student("Edeni",17)

print(studenti.name)
print(studenti.age)

studenti.name = "Driarti"
studenti.age = 15

print(studenti.name)
print(studenti.age)