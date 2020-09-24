# nasdaq_drone_challenge





Drone initializes the Controller, Gyroscope, OrientationSensor, and Engines.

The Controller manages the Gyroscope, OrientationSensor, and Engines. The bulk of logic is implemented in the Controller, as the inter-relationships between the hardware must be accounted for.

I use dependency injection to make it easier to manage all the different classes. The Engine, Gyro, and OrientationSensor dependencies are injected into the Controller, so any changes made in the dependencies are automatically reflected in the Controller.



There are many simplifying assumptions being made for this Drone challenge. Here's a list of some such assumptions.
- I only account for velocity (not position or acceleration, as the specs do not say that needs to be accounted for)
- As such, we assume that when engine power level is adjusted, the drone reaches its final velocity immediately (not gradually, in a continuous manner)
- The event lifecycle is as follows: The Controller commands the Engines, which effect the Orientation, which effect the Gyroscope. In real life, the relationship is not uni-directional. 
- Since I only account for velocity, I omit implementing a looping mechanism, PID control, and detailed physics/calculus calculations. Instead, I focus on capturing the architecture and requirements of the spec. 

You can see all my assumptions and simplifications in the python docstrings.

If power



Command Chains to Try Out


stabilize, take_off, stabilize

take_off, stabilize, land

take_off, land