from typing import TypeVar, List, Dict
import math
import argparse
import time

Engine = TypeVar('Engine')
Gyroscope = TypeVar('Gyroscope')
OrientationSensor = TypeVar('OrientationSensor')

class Drone():
    # using a static variable so that Controller, Gyro, and OrientationSensor can access the information
    # If you want to make more than 1 drone, you need to 
    drone_id = 1
    drone_statuses = dict()
    # drone_status = "off"
    def __init__(self, engines: int):
        # engines are initialized off, with a power of zero.
        # drone must take off from flat ground. In the future, look into initializing (pitch, roll) tuple.
        # drone must take off from a stationary platform. In the future, look into initializing (x, y, z) velocity tuple.
        self.drone_id = Drone.drone_id
        self.engines = [Engine() for i in range(engines)]
        self.gyroscope = Gyroscope(self.drone_id)
        self.orientation_sensor = OrientationSensor(self.drone_id)
        self.controller = Controller(self.drone_id, self.engines, self.gyroscope, self.orientation_sensor)
        Drone.drone_statuses[self.drone_id] = "off"
        Drone.drone_id += 1
        # when drone is initially constructed, it defaults to "off" status
        # self.drone_status = Drone.drone_status

    def take_off(self):
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
        self.controller.move_drone(direction)

    def stabilize(self):
        if Drone.drone_statuses[self.drone_id] == "off":
            print("The Drone is powered off, and so cannot hover :( ")
        elif Drone.drone_statuses[self.drone_id] == "moving":
            print("Stabilizing drone...")
            time.sleep(1)
            self.controller.stabilize_engines()
            print("The Drone is now hovering! Hurrah.")
        elif Drone.drone_statuses[self.drone_id] == "hovering":
            print("The Drone was already hovering.")
        return 0
    
    def land(self):
        print("Beginning landing procedure:")
        time.sleep(1)
        self.stabilize()
        print("Systems are a go. Proceed with landing.")
        time.sleep(1)
        self.controller.execute_landing_procedure()
        print("Landing...")
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
        # 50 is the power level that will stabilize the Drone.
        self.set_engine_power_levels([50 for i in range(len(self.engines))])
        Drone.drone_statuses[self.drone_id] = "hovering"
        self.update()
        return 0

    def execute_landing_procedure(self):
        # Go down at reduced speed, using default power level of 25.
        # Power level < 50 means the Drone will descend.
        self.set_engine_power_levels([25 for i in range(len(self.engines))])
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

    # def engine_power_levels(self):
    #     """ Returns list of power levels for all engines in increasing order of Engine number.
    #         In the case where there is an even number of engines:
    #             - Engine 1 is the front engine. 
    #             - Engine (n/2) + 1 will be the back engine.
    #     """
    #     return [e.power_indicator for e in self.engines]

    def update(self):
        # power_levels = Controller.engine_power_levels()
        self.orientation_sensor.update()
        Controller.orientation = dict(self.orientation_sensor)
        
        # print("HELLO", orientation)
        
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
    status_options = ("off", "on")

    def __init__(self, power_indicator: int = 0, engine_status: bool = 0):
        self.engine_id = Engine.engine_id
        self.power_indicator = power_indicator
        self.engine_status = engine_status
        Engine.engine_id += 1

    def __iter__(self):
        yield "engine_id", self.engine_id
        yield "power_indicator", self.power_indicator
        yield "engine_status", self.engine_status

    def readings(self):
        # print("Engine " + self.engine_id + " Status: " + )
        print("Engine {0}: ".format(self.engine_id))
        print(" Status: {0}".format(Engine.status_options[self.engine_status]))
        print(" Power: {0}".format(self.power_indicator))

    # def details(self):
    #     return {"engine_id": self.engine_id, "power_indicator": self.power_indicator, "engine_status": self.engine_status}
    
    # def status(self):
    #     return self.engine_status

    # def power_indicator(self):
    #     return self.power_indicator
    
    def set_power_level(self, new_power_level: int):
        self.power_indicator = new_power_level
        return 0

    def start(self, initial_power_level: int = 75):
        self.engine_status = 1
        self.power_indicator = initial_power_level
        return 0

    def stop(self):
        self.engine_status = 0
        self.power_indicator = 0
        return 0 

    
class Gyroscope():
    def __init__(self, drone_id: int, x: float = 0, y: float = 0, z: float = 0):
        self.drone_id = drone_id
        self.x = x # forward/backward velocity
        self.y = y # vertical velocity
        self.z = z # left/right velocity

    def readings(self):
        print("Gyrosope Measurements: ")
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
            self.x = 0
            self.y = Gyroscope.calculate_velocity(0)
            self.z = 0
        elif pitch == 0 and roll == 1: # the drone is moving left/right
            pass
        elif pitch == 1 and roll == 0: # the drone is moving forwards/backwords
            pass
        else:
            print("The Drone has escaped to the Z dimension??!!")
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
        # in clock-wise arrangement
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
            drone.move("left")
            drone.readings()
        elif command == "move_forward":
            drone.move("left")
            drone.readings()
        elif command == "move_backward":
            drone.move("left")
            drone.readings()
        elif command == "move_up":
            drone.move("left")
            drone.readings()
        elif command == "move_down":
            drone.move("left")
            drone.readings()
        elif command == "stabilize":
            drone.stabilize()
            drone.readings()
        elif command == "status":
            drone.readings() # readings include the Drone status.
        elif command == "land":
            drone.land()
            drone.readings()
        else:
            print("This command is not supported.")
    
    # args = parser.parse_args()


main()





# print("Welcome to Memorepo!")
    
#     parser = argparse.ArgumentParser(description='Interact with MemoRepo.')
#     parser.add_argument('--memorize', nargs="?", const="interface")
#     parser.add_argument('--recite', nargs="?", const="all")
#     args = parser.parse_args()

#     if args.memorize == "interface":
#         print("Input your sentences here:")
#         while True:
#             statement = input(">>> ")
#             # Do spacy preprocessing
#             # doc = nlp(statement)
#             # for token in doc:
#             #     print(token.text, token.lemma_, spacy.explain(token.tag_))
#             interface.memorize(str(statement))
#     elif args.memorize:
#         # memorize given sentence
#         print(args.memorize)
#         interface.memorize(str(args.memorize))

#     if args.recite == "all":
#         # get_all sentences that exist in memrepo
#         # arguments = all, some, specific
#         interface.recite(str(args.recite))
#         #write
#         # if args.
#         # if args.recall

# # drone has engines, 