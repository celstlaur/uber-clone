import datetime
import json
from distance import calculate_distance, convert_distance_to_seconds, convert_distance_to_minutes
from passengers import Passenger
from random import randint
import time
from math import isclose

MAXIMUM_RANDOM_VALUE = 1000
RANDOM_THRESHOLD = 905

DRIVER_COUNT = 0

DEFAULT_MILES_PER_HOUR = 10


class Driver:
    """Driver objects hold information about the driver, along
    with methods to "pickup" and "drive" a passenger to their
    destination.
    """

    def __init__(self, time_start, start_location: [float, float]):
        self.start_time = time_start
        self.end_time = None
        self.location = start_location
        self.drive_time = 0
        self.pickup_time = 0
        self.done_driving = False
        self.ride_profit = 0
        self.start_driving_time = None
        self.total_driving_time = None
        self.time_to_drive_last_passenger = None
        # global DRIVER_COUNT
        # self.driver_id = DRIVER_COUNT
        # DRIVER_COUNT += 1

    def __str__(self):
        return (
            f"Driver | Start time: {self.start_time} Current location: {self.location}"
        )
        
    # When drivers are compared with each other, they will compare against their start times.
    def __eq__(self, other):
        if not self.location == other.location:
            return False

        if not isclose(self.start_time, other.start_time):
            return False
        
        if not isclose(self.ride_profit, other.ride_profit):
            return False
        
        # if not self.driver_id == other.driver_id:
        #     return False
        
        return True

    def __lt__(self, other):
        return self.start_time < other.start_time

    def __le__(self, other):
        return self.start_time <= other.start_time

    def __ne__(self, other):
        return self.value != other.start_time

    def __gt__(self, other):
        return self.value > other.start_time

    def __ge__(self, other):
        return self.value >= other.start_time

    def start_timer(self,
                    given_time : float = None):
        """Starts the driving time timer for a driver.

        Does nothing if the timer has already started.

        If no given time is given, benchmark timer will be based on current time. This
        isn't recommended because the speed of the algorithm can influence the time for
        each driver.
        """
        if self.start_driving_time:
            return
        if (given_time):
            self.start_driving_time = given_time
        else:
            self.start_driving_time = time.time()

    def __pickup_passenger(
            self,
            passenger_location: tuple[float, float],
            passenger_pickup_distance: float = None,
            passenger_pickup_speed: float = DEFAULT_MILES_PER_HOUR,
    ) -> float:
        """Pickup a passenger.


        Note that if a pickup distance is not provided, we will calculate the distance
        ourselves, which may not be entirely accurate to the simulation.

        Args:
            passenger_location (tuple[float, float]): Latitude/Longitude location of the passenger
            passenger_pickup_distance (float): Distance to pickup a passenger. Optional, default= None
            passenger_pickup_speed (float): Speed to pickup a passenger. Optional, default = DEFAULT_MILES_PER_HOUR

        Returns:
            float: Distance it took to pickup a passenger.
        """
        if passenger_pickup_distance:
            pass_distance = passenger_pickup_distance
        else:
            pass_distance = calculate_distance(self.location, passenger_location)
        time_to_pickup = convert_distance_to_minutes(pass_distance, passenger_pickup_speed)
        self.pickup_time += time_to_pickup
        self.location = passenger_location

        return time_to_pickup

    def __drive_passenger_to_location(
            self,
            passenger_destination: tuple[float, float],
            dropoff_distance: float = None,
            dropoff_speed: float = DEFAULT_MILES_PER_HOUR,
    ) -> float:
        """Drive a passenger to their desired location.

        Note that if a dropoff distance is not provided, we will calculate the distance
        ourselves, which may not be entirely accurate to the simulation.

        Note that if a dropoff distance is not provided, we will calculate the distance
        ourselves, which may not be entirely accurate to the simulation.

        Args:
            passenger_destination (tuple[float, float]): Latitude/Longitude of the passengers desired location
            dropoff_distance (float): Distance to dropoff the passenger. Optional, default = DEFAULT_MILES_PER_HOUR
            
        Returns:
            float: Time taken to drive the passenger
        """
        if dropoff_distance:
            time_to_drive = convert_distance_to_minutes(dropoff_distance, dropoff_speed)
            self.drive_time += time_to_drive
        else:
            distance = calculate_distance(
                self.location, passenger_destination
            )
            time_to_drive = convert_distance_to_minutes(distance, dropoff_speed)
            self.drive_time += time_to_drive
        self.location = passenger_destination
        
        return time_to_drive

    def drive_passenger(
            self,
            passenger: Passenger,
            passenger_pickup_distance: float = None,
            dropoff_distance: float = None,
            pickup_speed: float = DEFAULT_MILES_PER_HOUR,
            dropoff_speed: float = DEFAULT_MILES_PER_HOUR,
            current_time: float = None,
    ):
        """Pickup a passenger and drive them to their destination.

        Note that there is a chance that the driver will be done driving
        at the end of driving this passenger. You can check the status of driving
        by using the check_if_done_driving method after running this command.
        (If you attempt to run this command with a driver who is done, it won't do anything)

        Note that this message will handle ending timers for both the passenger and the driver (if applicable)
        if they are enabled.

        Note that providing distance values for picking up a passenger is optional. If nothing is specified,
        we will calculate the distance, which may or may not be accurate to the simulation.
        
        For speed values, if nothing is specified, it will fall back to a default MPH as defined in the variable
        DEFAULT_MILES_PER_HOUR. Typically, you will want to specify this!
        
        Current time is used to calculate end times for the passenger and the driver if applicable. If not specified,
        the current time is decided using time.time(), which means that the runtime of the algorithm can influence
        our results.

        Args:
            passenger (Passenger): Passenger that the driver is picking up and driving
            passenger_pickup_distance (float): Distance needed to pickup a passenger. Optional, default = None
            dropoff_distance (float): Distance needed to drop off a passenger. Optional, default = None.
            pickup_speed (float): Speed to pickup a passenger. Optional, default= DEFAULT_MILES_PER_HOUR
            dropoff_speed (float): Speed to dropoff a passenger. Optional, default = DEFAULT_MILES_PER_HOUR.
        """
        if self.done_driving:
            print("Attempted to drive a passenger after finishing driving. Bad driver!")
            return -1
            print("Attempted to drive a passenger after finishing driving. Bad driver!")
            return -1

        pickup_time = self.__pickup_passenger(passenger.start_location, passenger_pickup_distance, pickup_speed)
        passenger.end_timer(additional_wait_time=pickup_time, given_stop_time=current_time)
        dropoff_time = self.__drive_passenger_to_location(passenger.desired_location, dropoff_distance, dropoff_speed)
        
        self.time_to_drive_last_passenger = pickup_time + dropoff_time
        
        passenger.destination_reached = True

        random_number = randint(0, MAXIMUM_RANDOM_VALUE)

        if random_number >= RANDOM_THRESHOLD:
            self.stop_driving(current_time)
        else:
            self.calculate_profit()

    def drive_passenger_T3(
            self,
            passenger: Passenger,
            passenger_pickup_time: float,
            dropoff_time: float,
            current_time : float = None,
    ):
        """Pickup a passenger and drive them to their destination.

        Note that there is a chance that the driver will be done driving
        at the end of driving this passenger. You can check the status of driving
        by using the check_if_done_driving method after running this command.
        (If you attempt to run this command with a driver who is done, it won't do anything)

        Note that this message will handle ending timers for both the passenger and the driver (if applicable)
        if they are enabled.

        Note that providing distance values for picking up a passenger is optional. If nothing is specified,
        we will calculate the distance, which may or may not be accurate to the simulation.
        
        Current time is used to calculate end times for the passenger and the driver if applicable. If not specified,
        the current time is decided using time.time(), which means that the runtime of the algorithm can influence
        our results.

        Args:
            passenger (Passenger): Passenger that the driver is picking up and driving
            passenger_pickup_time (float): How long it takes drivers to pickup a passanger (min)
            dropoff_distance (float): How long it takes drivers to dropoff a passanger (min)
        """
        if self.done_driving:
            print("Attempted to drive a passenger after finishing driving. Bad driver!")
            return -1

        passenger.end_timer(additional_wait_time=(passenger_pickup_time), given_stop_time=current_time)
        self.pickup_time += passenger_pickup_time

        self.__drive_passenger_to_location_T3(passenger.desired_location, dropoff_time)
        
        self.time_to_drive_last_passenger = passenger_pickup_time + dropoff_time

        passenger.destination_reached = True

        random_number = randint(0, MAXIMUM_RANDOM_VALUE)

        if random_number >= RANDOM_THRESHOLD:
            self.stop_driving(current_time)
        else:
            self.calculate_profit_T3()

    def __drive_passenger_to_location_T3(
            self,
            passenger_destination: tuple[float, float],
            dropoff_time: float,
    ):
        """Drive a passenger to their desired location.

        Args:
            dropoff_time(float): Time to dropoff the passenger
        """
        if dropoff_time:
            self.drive_time += dropoff_time
            self.location = passenger_destination

    def stop_driving(self,
                     given_stop_time : float = None
                     ):
        """Does end of driving operations for the driver,
        such as setting the done driving flag and calculating profit.
        
        If the stop time is not given, then the given stop time will default to time.time()
        
        Args:
            given_stop_time (float, optional): Given stop time for the driver. Defaults to None.
        """
        # save benchmark results
        self.done_driving = True
        self.__stop_timer(given_stop_time)
        self.calculate_profit()
        
    def __stop_timer(self,
                   given_time: float = None
                   ):
        """Stops the drive time timer.
        
        It is recommend that a time is given. If not, time.time() will be used
        instead, meaning that the speed of the algorithm can influence drive times.
        
        Not intended for use outside of the Driver class itself.

        Args:
            given_time (float, optional): Time to stop the timer at. Defaults to None.
        """
        if self.start_driving_time is not None:
            if (given_time):
                self.total_driving_time = (given_time - self.start_driving_time) / 60
            else:
                self.total_driving_time = (time.time() - self.start_driving_time) / 60

    def calculate_profit(self):
        """Calculates the current ride profit for a driver."""
        # self.ride_profit = convert_distance_to_seconds(self.drive_distance) - convert_distance_to_seconds(
        #     self.pickup_distance)
        self.ride_profit = self.drive_time - self.pickup_time

    def calculate_profit_T3(self):
        """Calculates the current ride profit for a driver."""
        # self.ride_profit = self.drive_distance - self.pickup_distance  # SHOULDN'T profit be cumulative ($10 ride 1 and $20 ride 2 = $30 in total)
        self.ride_profit = self.drive_time - self.pickup_time

    def check_if_done_driving(self) -> bool:
        """Returns whether the driver is done driving or not.

        Returns:
            bool: True if done driving, False if not
        """
        return self.done_driving

    def get_driving_time(self) -> float:
        """Returns the time this driver spent driving.

        If the driver is still currently driving, this will
        return None.

        Will return None if the starting time was never initialized as well.
        
        Returns in Minutes

        Returns:
            float: Total time the driver has spent working/driving
        """
        return self.total_driving_time + self.drive_time + self.pickup_time

    def get_ride_profit(self) -> float:
        """Returns the profit that the driver has received thus far.

        Returns:
            float: Drivers' current profit
        """
        return self.ride_profit

    def get_start_time(self) -> float:
        """Returns the time this driver started driving.

        Returns:
            float: Time this driver started driving.
        """
        return self.start_time

    # def get_id(self) -> int:
    #     """Returns the id of this driver

    #     Returns:
    #         int: id
    #     """
    #     return self.driver_id

    def find_nearest_node(self, point):
        """Calculates the nearest node from a given point to one in the road network

        Args:
            point (tuple): Point that passenger is requesting

        Returns:
            tuple: Nearest node in the road network to the requested point with id and its coordinates
        """
        # Placeholder for the nearest node and its distance
        nearest_node = None
        nearest_distance = float('inf')

        # Load road network
        with open('node_data.json', 'r') as file:
            node_data = json.load(file)

        # Iterate over all nodes and calculate the distance
        for node_id, node_info in node_data.items():
            # Extract the node's coordinates
            node_lat, node_lon = node_info['lat'], node_info['lon']
            node_coords = (node_lat, node_lon)

            # Calculate distance from the provided point to the current node
            distance = calculate_distance(point, node_coords)

            # If this node is closer than the current nearest, update the nearest information
            if distance < nearest_distance:
                nearest_node = node_id
                nearest_distance = distance
                best_lat = node_lat
                best_lon = node_lon

        return nearest_node
    def get_start_hour(self) -> int:
        """Get the hour from the start_time."""
        dt = datetime.datetime.fromtimestamp(self.start_time)
        return dt.hour

    def get_drivetime_for_last_passenger(self):
        return self.time_to_drive_last_passenger