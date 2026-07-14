#%%
# ------------------------------------------------------------
# Unit 3 - Implementing the Factory Method Pattern
# ------------------------------------------------------------

class Car:
    def drivetrain(self):
        return "RWD"
    def drive(self):
        print(f"Driving the Car")


class Sedan(Car):
    def drive(self):
        print(f"Driving my {self.__class__.__name__} in {self.drivetrain()}")

class SUV(Car):
    def drivetrain(self):
        return "4WD"    
    def drive(self):
        print(f"Driving their {self.__class__.__name__} in {self.drivetrain()}")

class Hatchback(Car):
    def drivetrain(self):
        return "FWD"     
    def drive(self):
        print(f"Driving a {self.__class__.__name__} in {self.drivetrain()}")

class CarFactory:
    def create_car(self):
        pass

class SedanFactory(CarFactory):
    def create_car(self):
        return Sedan()

class SUVFactory(CarFactory):
    def create_car(self):
        return SUV()

class HatchbackFactory(CarFactory):
    def create_car(self):
        return Hatchback()        

factories = [SedanFactory(),SUVFactory(),HatchbackFactory()]

for factory in factories:
    car = factory.create_car()
    car.drive()

# %%
