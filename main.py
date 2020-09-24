import argparse
import math
import random
import time
from typing import TypeVar, List, Dict


Drone = TypeVar('Drone')
Engine = TypeVar('Engine')
Gyroscope = TypeVar('Gyroscope')
OrientationSensor = TypeVar('OrientationSensor')


class Drone():

    drone_id = 1
    drone_statuses = dict()

    def __init__(self, engines: int):
        """ Engines are initialized off, with a power of zero.
            Drone must take off from flat ground. In the future, look into initializing (pitch, roll) tuple.
            Drone must take off from a stationary platform. In the future, look into initializing (x, y, z) velocity tuple.
        """
        self.drone_id = Drone.drone_id
        self.engines = [Engine() for i in range(engines)]
        self.gyroscope = Gyroscope(self.drone_id)
        self.orientation_sensor = OrientationSensor(self.drone_id)
        self.controller = Controller(self.drone_id, self.engines, self.gyroscope, self.orientation_sensor)
        self.sabotaged = False
        Drone.drone_statuses[self.drone_id] = "off"
        Drone.drone_id += 1

    def systems_check(self):
        """ Check hardware to see everything is functional.
            Currently only checks the Engines.
        """
        for engine in self.engines:
            if engine.engine_status == "destroyed":
                self.sabotaged = True
        return 0

    def take_off(self):
        print("Running systems check...")
        self.systems_check()
        time.sleep(.5)
        
        if self.sabotaged:
            print("\33[31mWARNING: The Drone is sabotaged, and cannot take off!!\33[0m")
            return 1
        
        if Drone.drone_statuses[self.drone_id] == "off":
            print("Turning the Drone on...")
            time.sleep(.5)
            print("Starting Drone engines...")
            time.sleep(1)
            self.controller.start_engines()
            print("The Drone has taken off!")
            time.sleep(.5)
        else:
            print("The Drone has already taken off...")
        return 0
       
    def readings(self):
        print()
        print("Drone Status: {0}".format(Drone.drone_statuses[self.drone_id]))
        self.orientation_sensor.readings()
        self.gyroscope.readings()
        for eng in self.engines:
            eng.readings()
        print()

    def status(self):
        return Drone.drone_statuses[self.drone_id]

    def move(self, direction: str):
        if Drone.drone_statuses[self.drone_id] == "off":
            if self.sabotaged:
                print("\33[31mWARNING: The Drone is sabotaged. The Drone must be fixed before it can take off! \33[0m")
            print("The Drone is powered off, and so cannot move :( ")
        else:
            if self.sabotaged:
                print("\33[31mSOS: The Drone is sabotaged. Execute emergency landing procedure immediately!! \33[0m")
                self.land()
                return 1
            print("Moving Drone {0}...".format(direction))
            time.sleep(1)
            self.controller.move_drone(direction)
            print("The Drone is now moving {0}!".format(direction))
        return 0

    def stabilize(self):
        if Drone.drone_statuses[self.drone_id] == "off":
            if self.sabotaged:
                print("\33[31mWARNING: The Drone is sabotaged. The Drone must be fixed before it can take off! \33[0m")
            print("The Drone is powered off, and so cannot hover :( ")
        elif Drone.drone_statuses[self.drone_id] == "moving":
            if self.sabotaged:
                print("\33[31mSOS: The Drone is sabotaged. Execute emergency landing procedure immediately!! \33[0m")
                self.land()
                return 1
            print("Stabilizing drone...")
            time.sleep(1)
            self.controller.stabilize_engines()
            print("The Drone is now hovering! Hurrah.")
        elif Drone.drone_statuses[self.drone_id] == "hovering":
            if self.sabotaged:
                print("\33[31mSOS: The Drone is sabotaged. Execute emergency landing procedure immediately!! \33[0m")
                self.land()
                return 1
            print("The Drone was already hovering.")
        return 0
    
    def land(self):
        if Drone.drone_statuses[self.drone_id] == "off":
            if self.sabotaged:
                print("\33[31mWARNING: The Drone is sabotaged. The Drone must be fixed before it can take off! \33[0m")
            print("The Drone never left ground in the first place.")
        else:
            if self.sabotaged:
                print("\33[31mExecuting emergency landing procedure!! \33[0m")
                time.sleep(1)
                self.controller.execute_emergency_landing_procedure()
                return 1
            print("Beginning landing procedure:")
            time.sleep(1)
            self.stabilize()
            print("Systems are a go. Proceed with landing.")
            time.sleep(1)
            self.controller.execute_landing_procedure()
            print("Landing...")
        return 0

    def update(self):
        self.systems_check()
        if self.sabotaged:
            if Drone.drone_statuses[self.drone_id] == "off":
                print("\33[31mWARNING: The Drone is sabotaged, and needs to be fixed!! \33[0m")    
            else:
                print("\33[31mSOS: The Drone is sabotaged, and needs to make an emergency landing!! \33[0m")
                self.land()
        return 0


class Controller():
    engine_power_levels = list()
    orientation = dict()

    def __init__(self, drone_id: int, engines: List[Engine], gyroscope: Gyroscope, orientation_sensor: OrientationSensor):
        self.drone_id = drone_id
        self.engines = engines
        self.gyroscope = gyroscope
        self.orientation_sensor = orientation_sensor

    def set_engine_power_levels(self, new_power_levels: List[int]):
        for i in range(len(new_power_levels)):
            self.engines[i].set_power_level(new_power_levels[i])
        Controller.engine_power_levels = new_power_levels
        return 0
 
    def start_engines(self):
        """ Starts all engines, turning them on and initializing their power levels to 50.
        """
        for engine in self.engines:
            engine.start()
            Controller.engine_power_levels.append(engine.power_indicator)
        Drone.drone_statuses[self.drone_id] = "moving"
        self.update()
        return 0

    def stabilize_engines(self):
        """ 50 is the power level that will stabilize the Drone."""
        self.set_engine_power_levels([50 for i in range(len(self.engines))])
        Drone.drone_statuses[self.drone_id] = "hovering"
        self.update()
        return 0

    def execute_landing_procedure(self):
        """ Go down at reduced speed, using default power level of 25.
            Power level < 50 means the Drone will descend.
        """
        self.set_engine_power_levels([25 for i in range(len(self.engines))])
        Drone.drone_statuses[self.drone_id] = "moving"
        self.update()
        return 0

    def execute_emergency_landing_procedure(self):
        memo = None
        for i in range(len(self.engines)):
            if self.engines[i].engine_status == "destroyed":
                memo = (i + 2) % 4 # assuming 4 engines
            else:
                self.engines[i].set_power_level(25)
        if memo:
            self.engines[memo].stop()
        Drone.drone_statuses[self.drone_id] = "moving"
        self.update()
        return 0

    def move_drone(self, direction: str):
        """ Use preconfigured engine settings to move forward/backward/etc...
            - Engine power requirements to move forward = [50, 50, 75, 50] 
            - Engine power requirements to move backward = [75, 50, 50, 50]
            - Engine power requirements to move left = [50, 75, 50, 50]
            - Engine power requirements to move right = [50, 50, 50, 75]
            - Engine power requirements to move up = [75, 75, 75, 75]
            - Engine power requirements to move down = [25, 25, 25, 25]
        """
        if direction == "forward":
            power_level_requirement = [50, 50, 75, 50]
        elif direction == "backward":
            power_level_requirement = [75, 50, 50, 50]
        elif direction == "left":
            power_level_requirement = [50, 75, 50, 50]
        elif direction == "right":
            power_level_requirement = [50, 50, 50, 75]
        elif direction == "up":
            power_level_requirement = [75, 75, 75, 75]
        elif direction == "down":
            power_level_requirement = [25, 25, 25, 25]
        self.set_engine_power_levels(power_level_requirement)
        Drone.drone_statuses[self.drone_id] = "moving"
        self.update()
        return 0

    def update(self):
        Controller.engine_power_levels = [engine.power_indicator for engine in self.engines]
        self.orientation_sensor.update()
        Controller.orientation = dict(self.orientation_sensor)
        self.gyroscope.update()
        return 0


class Engine():
    """ Engines are identified from 1 to n.
        Each engine powers a rotary propeller system.
        Engine 1 (and corresponding propeller system) are located at the front of the drone.
        Engine 2 to n are located around the drone, equally spaced around the circumference of the drone.
        Assume the Drone and Propelling system is callibrated, such that
            - Engine power level > 50, portion of drone containing engine should lift.
            - Engine power level < 50, portion of drone containing engine should drop.
            - Engine power level == 50, portion of drone containing engine should not move.
    """
    engine_id = 1

    def __init__(self, power_indicator: int = 0, engine_status: str ="off"):
        self.engine_id = Engine.engine_id
        self.power_indicator = power_indicator
        self.engine_status = engine_status
        Engine.engine_id += 1

    def __iter__(self):
        yield "engine_id", self.engine_id
        yield "power_indicator", self.power_indicator
        yield "engine_status", self.engine_status

    def readings(self):
        print("Engine {0}: ".format(self.engine_id))
        print(" Status: {0}".format(self.engine_status))
        print(" Power: {0}".format(self.power_indicator))
   
    def set_power_level(self, new_power_level: int):
        self.power_indicator = new_power_level
        return 0

    def start(self, initial_power_level: int = 75):
        self.engine_status = "on"
        self.power_indicator = initial_power_level
        return 0

    def stop(self):
        self.engine_status = "off"
        self.power_indicator = 0
        return 0 

    
class Gyroscope():
    def __init__(self, drone_id: int, x: float = 0, y: float = 0, z: float = 0):
        self.drone_id = drone_id
        self.x = x # forward/backward velocity
        self.y = y # vertical velocity
        self.z = z # left/right velocity

    def readings(self):
        print("Gyroscope Measurements: ")
        if Drone.drone_statuses[self.drone_id] == "off":
            print(" X Velocity: {0}".format("N/A"))
            print(" Y Velocity: {0}".format("N/A"))
            print(" Z Velocity: {0}".format("N/A"))
        else: 
            print(" X Velocity: {0}".format(self.x))
            print(" Y Velocity: {0}".format(self.y))
            print(" Z Velocity: {0}".format(self.z))
        return 0
    
    @staticmethod
    def calculate_velocity(angle_from_reference_plane: float):
        """ Equilibrium power = 50 (the Drone will not rise or fall i.e. it hovers at a fixed height) 
            This is not a realistic calculation based off of physics. It is a simplification.
            In the future, can write a better calculate_velocity function.
        """
        average_power = sum(Controller.engine_power_levels)/len(Controller.engine_power_levels)
        radians = (angle_from_reference_plane * 2 * math.pi)/360 
        magnitude = (average_power - 50) * math.cos(radians)
        return magnitude

    def update(self):
        """ Simplifying Assumptions:
            - Since yaw is not considered in these calculations, the Z Velocity vector will always be 0.
              In other words, the X Velocity vector is sufficient.
              It is not possible to calculate the Z Velocity vector without yaw. There is no frame of reference.
            - The Drone can only move left, right, backwards, forwards, up, and down.
              That means, it must be true that at least one of the two measurements (pitch, roll) is 0.
              Furthermore, I do not have to code for diagonal directions.
        """
        pitch = Controller.orientation["pitch"]
        roll = Controller.orientation["roll"]
        if pitch == 0 and roll == 0: # the drone is moving up/down
            self.x = 0.0
            self.y = Gyroscope.calculate_velocity(0)
            self.z = 0.0
        elif pitch == 0 and roll != 0: # the drone is moving left/right
            self.x = Gyroscope.calculate_velocity(roll)
            self.y = 0.0
            self.z = 0.0
        elif pitch != 0 and roll == 0: # the drone is moving forwards/backwords
            self.x = Gyroscope.calculate_velocity(pitch)
            self.y = 0.0
            self.z = 0.0
        else:
            print("The Drone has escaped to the Z dimension??!!")
            if abs(pitch) >= abs(roll):
                self.x = Gyroscope.calculate_velocity(pitch)
                self.y = Gyroscope.calculate_velocity(90 - pitch)
                self.z = "???"
                return 1
            else:
                self.x = Gyroscope.calculate_velocity(roll)
                self.y = Gyroscope.calculate_velocity(90 - roll)
                self.z = "???"
                return 1
        return 0


class OrientationSensor():
    def __init__(self, drone_id: int, pitch: float = 0, roll: float = 0):
        self.drone_id = drone_id
        self.pitch = pitch
        self.roll = roll

    def __iter__(self):
        yield "pitch", self.pitch
        yield "roll", self.roll

    def update(self):
        """ This update function will only work for a drone with 4 engines.
            Simplifying the physics. 
                - Take the difference between the power levels to calculate pitch and roll angles.
                - The most extreme power level diff would be +/- 100. Limit the max angle to 50 by dividing the diff by 2.
                - Angle = (power_level_A - power_level_B)/2
        """
        # in clock-wise arrangement, starting from the front engine:
        front_engine = Controller.engine_power_levels[0]
        right_engine = Controller.engine_power_levels[1]
        back_engine = Controller.engine_power_levels[2]
        left_engine = Controller.engine_power_levels[3]

        self.pitch = (front_engine - back_engine)/2.0
        self.roll = (right_engine - left_engine)/2.0

    def readings(self):
        print("Orientation: ")
        if Drone.drone_statuses[self.drone_id] == "off":
            print(" Pitch: {0}".format("N/A"))
            print(" Roll: {0}".format("N/A"))
        else: 
            print(" Pitch: {0}".format(self.pitch))
            print(" Roll: {0}".format(self.roll))
        return 0


class God():
    def __init__(self, drone: Drone):
        self.drone = drone

    def destroy_engine(self):
        if self.drone.sabotaged:
            print("Sorry God, but you're only allowed to inflict one Engine's worth of damage per simulation.")
            return 1
        else:
            selected_engine = random.randint(0, len(self.drone.engines)-1)
            print("God zaps Engine {0}.".format(selected_engine+1))
            self.drone.engines[selected_engine].engine_status = "destroyed"
            self.drone.engines[selected_engine].power_indicator = 0
            self.drone.update()
        return 0
        
    def sabotage_take_off(self):
        if Drone.drone_statuses[self.drone.drone_id] != "off":
            print("God was too late, and couldn't sabotage the Drone before it took off. Whew!")
            return 1
        else:
            if self.drone.sabotaged:
                print("Sorry God, but you're only allowed to inflict one Engine's worth of damage per simulation.")
                return 1
            else:
                self.destroy_engine()        
        return 0

    def nudge_drone(self):
        if Drone.drone_statuses[self.drone.drone_id] == "off":
            print("The Drone is off, and is pretty unnudgeable right now.")
        else:
            print("The Drone has been nudged in all sorts of strange ways!")
            time.sleep(2)
            self.drone.orientation_sensor.pitch += random.uniform(-5, 5)
            self.drone.orientation_sensor.roll += random.uniform(-5, 5)
            Controller.orientation = dict(self.drone.orientation_sensor)
            self.drone.gyroscope.update()
            self.drone.readings()
            print("\n\33[32mRecalibrating drone...\33[0m\n")
            time.sleep(1)
            self.drone.stabilize()    


def main():
    print("Welcome to Drone Simulator 2020!")
    print()
    print("The following Drone functions are available to you: ")
    print("take_off, move_left, move_right, move_forward, move_backward, move_up, move_down, stabilize, status, land")
    print()
    print("The following 'God' functions are available to you: ")
    print("destroy_engine, sabotage_take_off, nudge_drone")
    print()

    drone = Drone(4)
    god = God(drone)

    parser = argparse.ArgumentParser(description='Interact with your Drone.')
    while True:
        command = input(">>> ")
        if command == "take_off":
            drone.take_off()
            drone.readings()
        elif command == "move_left":
            drone.move("left")
            drone.readings()
        elif command == "move_right":
            drone.move("right")
            drone.readings()
        elif command == "move_forward":
            drone.move("forward")
            drone.readings()
        elif command == "move_backward":
            drone.move("backward")
            drone.readings()
        elif command == "move_up":
            drone.move("up")
            drone.readings()
        elif command == "move_down":
            drone.move("down")
            drone.readings()
        elif command == "stabilize":
            drone.stabilize()
            drone.readings()
        elif command == "status":
            drone.readings() # readings include the Drone status.
        elif command == "land":
            drone.land()
            drone.readings()
        elif command == "destroy_engine":
            god.destroy_engine()
            drone.readings()
        elif command == "sabotage_take_off":
            god.sabotage_take_off()
            drone.readings()
        elif command == "nudge_drone":
            god.nudge_drone()
            drone.readings()
        else:
            print("This command is not supported. \n")
    

main()
