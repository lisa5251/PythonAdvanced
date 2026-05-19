
class Personi:

    def __init__(self,name,age,weight,height):
        self.name=name
        self.age = age
        self.weight = weight
        self.height = height

    def get_name(self):
        return self.name

    def get_age(self):
        return self.age

    def get_weight(self):
        return self.weight

    def get_height(self):
        return self.height

    def weight_status(self):
        bmi = self.weight / (self.height ** 2)

        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    def age_status(self):
        if self.age < 13:
            return "Child"
        elif self.age < 18:
            return "Teen"
        else:
            return "Adult"
