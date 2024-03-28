import time
from math import isclose
import json
from distance import calculate_distance
import datetime

PASSENGER_COUNT = 0

class Passenger:
    """Passenger Class holds necessary information about a passenger
    at NotUber.
    """

    def __init__(
        self,
        given_start_time: float,
        start_location: [float, float],
        desired_location: [float, float],
    ):
        self.start_time = given_start_time
        self.benchmark_time_start = None
        self.start_location = start_location
        self.desired_location = desired_location
        self.destination_reached = False
        self.total_waiting_time = None
        self.total_passenger_time = None
        # global PASSENGER_COUNT
        # self.passenger_id = PASSENGER_COUNT
        # PASSENGER_COUNT += 1
        
        # timer pause related instance variables
        self.pause_time_start = None
        self.unneeded_time = None
        self.paused = False


    def __str__(self):
        return f"Passenger | start_time {self.start_time} : start location {self.start_location} : desired location {self.desired_location}"

    def __eq__(self, other):
        return isclose(self.start_time, other.start_time)

    def __lt__(self, other):
        return self.start_time < other.start_time

    def initialize_waiting_time(self):
        """Initialize the waiting time for a passenger."""
        self.start_waiting_time = time.time(self.time)

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
        """Starts a timer for how long a passenger has been waiting.

        If the timer has already started, this method will do nothing.
        
        If no given time is given, benchmark timer will be based on current time. This
        isn't recommended because the speed of the algorithm can influence the time for
        each passenger.
        
        Args:
            given_time (float): Time to start the passenger at. Optional, default is None.
        """
        if self.benchmark_time_start:
            # print("Ruh-roh, None")
            # print(self.benchmark_time_start)
            return
        if (given_time):
            self.benchmark_time_start = given_time
        else:
            self.benchmark_time_start = time.time()

    def end_timer(self,
                  additional_wait_time: float = None,
                  given_stop_time: float = None
                  ):
        """Stop the timer for the current waiting start_time.

        If the timer has already been stopped, this method won't do anything.

        If there is an additional factor that must be considered in the wait time,
        it can be added as an optional argument.
        
        Note that given_stop_time is optional, but it is recommended to use one. Without a given
        stop time, the timer will take the stop time using the time.time() method, which means
        that the speed of the algorithm can influence the stop time of the timer.

        Args:
            additional_wait_time (float): Factor in additional wait time. Optional, default is None.
            given_stop_time (float): Time we wish to stop the timer at. Optional, default is None.
        """
        if self.total_waiting_time:
            return
        if self.benchmark_time_start:
            if (given_stop_time):
                self.total_waiting_time = (given_stop_time - self.benchmark_time_start) / 60
            else:
                self.total_waiting_time = (time.time() - self.benchmark_time_start) / 60

            if additional_wait_time:
                self.total_waiting_time += additional_wait_time

    def get_start_hour(self) -> int:
        """Get the hour from the start_time."""
        dt = datetime.datetime.fromtimestamp(self.start_time)
        return dt.hour
    
    def get_start_time(self) -> float:
        """Get the hour from the start_time."""
        return self.start_time

    def end_waiting_time(self):
        """Stop the timer for the current waiting start_time."""
        if self.start_time is not None:
            self.total_waiting_time = time.time() - self.start_time

    def get_total_waiting_time(self) -> float:
        """Get the total waiting time of a passenger.
        Note that if total waiting time does not exist yet,
        this will return None.

        Returns:
            float: Passengers' total waiting time until picked up
        """
        if (self.unneeded_time):
            return self.total_waiting_time - self.unneeded_time
        return self.total_waiting_time

    def get_start_waiting_time(self) -> float:
        """Returns the starting wait start_time for the passenger if initialized

        Returns:
            float: starting wait start_time for the passenger
        """
        return self.start_time

    def calculate_total_passenger_time(self, driving_time: float = None):
        """Calculates the total time the passenger was a passenger,
        from initial waiting to arrival at destination, factoring in a given
        driving time if desired.
        
        Note that if no driving time is provided, this is the same as the total
        waiting time for the passenger, aka the output of get_total_waiting_time

        Args:
            driving_time (float): Time taken to drive. Optional, default is None.

        Returns:
            _type_: Returns total passenger time.
                    If total waiting time does not exist, returns None.
        """
        if self.total_waiting_time is not None:
            if driving_time is None:
                self.total_passenger_time = self.get_total_waiting_time()
            else:
                self.total_passenger_time = self.get_total_waiting_time() + driving_time
            return self.total_passenger_time
        else:
            return None
        
    # def get_id(self) -> int:
    #     """Returns the id of this passenger

    #     Returns:
    #         int: id
    #     """
    #     return self.passenger_id

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
        
        return nearest_node, best_lat, best_lon
    
    def find_nearest_pickup_point(self):
        """Calculates the nearest node from requested pickup location to one in the road network

        Returns:
            tuple: Nearest node in the road network to the pickup location with id and its coordinates
        """
        return self.find_nearest_node(self.start_location)

    def find_nearest_dropoff_point(self):
        """Calculates the nearest node from requested dropoff location to one in the road network

        Returns:
            tuple: Nearest node in the road network to the dropoff location with id and its coordinates
        """
        return self.find_nearest_node(self.desired_location)
    
    # Pausing the timer should no longer be necessary with the timer changes.
    
    # def pause_timer(self):
    #     self.paused = True
    #     self.pause_time_start = time.time()

    # def resume_timer(self):
    #     if not self.paused:
    #         return
    #     self.unneeded_time = time.time() - self.pause_time_start
    #     self.paused = False
