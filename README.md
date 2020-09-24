# NASDAQ Drone Challenge

## High-level Overview

The Drone class initializes the Controller, Gyroscope, OrientationSensor, and Engine classes.

The Controller manages the Gyroscope, OrientationSensor, and Engines, as well as the inter-relationships between the entities.

I use dependency injection to make it easier to manage all the different classes. The Engine, Gyro, and OrientationSensor dependencies are injected into the Controller, so any changes made in the dependencies are automatically reflected in the Controller.

I also use static variables, so that information that multiple classes rely on can be update globally. I try to minimize the number of parameters being passed by any class or instance method. This improves readibility, and makes refactoring more efficient.

## Simplifying Assumptions

There are many simplifying assumptions being made for this Drone challenge. Here's a list of some such assumptions.
- I only account for velocity (not position or acceleration, as the specs do not say that needs to be accounted for).
- I assume that when the engine powers are adjusted, the drone reaches its final velocity immediately (not gradually, in a continuous manner). This minimizes the need for physics calculations.
- The event lifecycle is as follows: The Controller commands the Engines, which effect the Orientation, which effect the Gyroscope. In real life, the relationship is not uni-directional. 
- Since I only account for velocity, I omit implementing a looping mechanism, PID control, and detailed physics/calculus calculations. Instead, I focus on capturing the architecture and requirements of the spec. 

You can see more detailed assumptions and simplifications in the Python docstrings.

## Instructions

Run `python3 main.py` in your terminal.

Use the following commands to direct the Drone:
- take_off
- move_forward
- move_backward
- move_left
- move_right
- move_up
- move_down
- stabilize
- status
- land

There are certain actions you can do, called "God" commands. They let you control the fate of the Drone in ways it was not designed for. These commands represent how, in the real world, edge cases and accidents are prone to happen.

The following "God" commands are:
- destroy_engine
- sabotage_take_off
- nudge_drone

Take some time to play around with the Drone in the terminal. Try to find hidden interactions, and experiment with different combinations of command sequences!

## Example Command Sequences to Test
- stabilize, take_off, stabilize
- destroy_engine, take_off
- take_off, destroy_engine
- take_off, sabotage_take_off
- move_left, take_off
- take_off, move_left, nudge_drone
- nudge_drone, take_off
- take_off, destroy_engine, destroy_engine
- etc...
