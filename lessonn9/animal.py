class Animal:


    def sound(self):
        print("sound of the animal")

class Dog(Animal):
    def sound(self):
        print("woof! woof!")

class Cat(Animal):
    def sound(self):
        print("mewwww mewwww")

animal1 = Animal()
animal1.sound()

animal2 = Dog()
animal2.sound()

animal3 = Cat()
animal3.sound()