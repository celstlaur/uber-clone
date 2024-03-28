import csv
from datetime import timedelta
import datetime
from datetime import timedelta
import datetime
import heapq
import json
from passengers import Passenger
from drivers import Driver
from roads import Roads
import time
import heapq
from distance import calculate_distance

ARBITRARY_BIG_NUMBER = 65536

def T3():
    passengers = []
    with open("passengers.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            passenger = Passenger(
                time.mktime(time.strptime(row["Date/Time"], "%m/%d/%Y %H:%M:%S")),
                (float(row["Source Lat"]), float(row["Source Lon"])),
                (float(row["Dest Lat"]), float(row["Dest Lon"])),
            )
            passengers.append(passenger)

    drivers = []
    with open("drivers.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            driver = Driver(
                time.mktime(time.strptime(row["Date/Time"], "%m/%d/%Y %H:%M:%S")),
                (float(row["Source Lat"]), float(row["Source Lon"])),
            )
            drivers.append(driver)

    road_list = Roads()
    with open("edges.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            weekday_list = []
            weekend_list = []
            for index in range(24):
                weekday = "weekday_" + str(index)
                weekend = "weekend_" + str(index)
                if row[weekend] is not None:
                    weekday_list.append(float(row[weekday]))
                    weekend_list.append(float(row[weekend]))

            road_list.add_road(
                row["start_id"],
                row["end_id"],
                float(row["length"]),
                weekday_list,
                weekend_list,
            )

    node_map = dict()
    with open("node_data.json", "r") as file:
        data = json.load(file)
        for node_id in data:
            node_struct = (data[node_id]["lat"], data[node_id]["lon"])
            # print(node_struct)
            # print("Node ID: %s \n",node_id)
            node_map[node_struct] = node_id


    def is_weekday_or_weekend(date):
        # Get the weekday index (Monday is 0, Sunday is 6)
        dt = datetime.datetime.fromtimestamp(date)
        weekday_index = dt.weekday()

        # Check if it's a weekday (Monday to Friday)
        if 0 <= weekday_index <= 4:
            return 'Weekday'
        else:
            return 'Weekend'


    def get_edge_weight(start_node: str, end_node: str, weekend_weekday:str, hour) -> float:
        """Get the edge weight (travel time) between two nodes for a specific hour.

        Args:
            start_node (str): Start node's ID.
            end_node (str): End node's ID.
            hour (int): Hour of the day (0-23).

        Returns:
            float: Edge weight (travel time) between the nodes for the given hour.
        """
        # DETERMINE WHETHER TO CALL WEEKDAY SPEED OR WEEKEND SPEED
        length = road_list.get_road_length(start_node,end_node)

        if(weekend_weekday=='Weekday'):
            speed = road_list.get_weekday_speed(start_node,end_node, hour = hour)
            #print("Weekday")
        else:
            speed = road_list.get_weekend_speed(start_node,end_node, hour = hour)
            #print("Weekend")
        # print("LENGTH %f"%length)
        # print("speed %f"% speed)
        # print("Time %f"%(length/speed))

        #length/speed= hrs it takes to drive their
        return (length/speed)*60

    # MY Algorithm
    def calculate_estimated_time(start_node,end_node, weekend_weekday, hour, min_pickup_time) -> float:
        """Calculate the estimated time for the driver to reach the passenger.

        Returns:
            float: Estimated time for the driver to reach the passenger.
        """
        if start_node is None or end_node is None:
            print("Invalid start or end node.")
            return float('inf')  # Return infinity if nodes are not valid.

        # Dijkstra's algorithm to find the shortest path
        min_time_to_node = {}  # Initialize an empty dictionary
        min_time_to_node[start_node] = 0  # Current time serves as the starting time

        priority_queue = [(0, start_node)]
        visited_nodes = set()

        while priority_queue:
            current_time, current_node = heapq.heappop(priority_queue)


            if current_node in visited_nodes:
                continue
            visited_nodes.add(current_node)

            if current_node == end_node:
                # Found the shortest path to the destination node
                return min_time_to_node[end_node]

            if min_time_to_node[current_node] > min_pickup_time:
                return float('inf')

            # Explore neighbors dynamically
            for neighbor_node in road_list.get_neighbors(current_node):
                if neighbor_node in visited_nodes:
                    continue

                edge_weight = get_edge_weight(current_node, neighbor_node, weekend_weekday, hour) #when driver is picking up passanger
                if edge_weight is not None:
                    # Calculate the arrival time at the neighbor node
                    arrival_time = current_time + edge_weight

                    # Update the minimum time to reach the neighbor node
                    if neighbor_node not in min_time_to_node or arrival_time < min_time_to_node[neighbor_node]:
                        min_time_to_node[neighbor_node] = arrival_time
                        heapq.heappush(priority_queue, (arrival_time, neighbor_node))

        return float('inf')  # Return infinity if no path is found

    heapq.heapify(drivers)
    heapq.heapify(passengers)


    # Create data structures in use of the algorithm.
    available_drivers = []
    available_passengers = []

    done_drivers = []
    done_passengers = []

    drivers_size = len(drivers)
    total_drivers = drivers_size
    passengers_size = len(passengers)
    total_passengers = passengers_size

    print(f"Number of drivers in total: {drivers_size}")
    print(f"Number of passengers in total: {passengers_size}")

    curr_time = passengers[0].get_start_waiting_time()
    passengers_driven = 0

    runtime_start = time.time()
    start_time = time.time()

    while passengers or available_passengers:
        # We cannot just let all the passengers/drivers loose at once in the queue, so
        # we are manually incrementing the time by each minute and adding relevant
        # passengers to the queue.
        # if(passengers_driven >= 300):
        #     break
        curr_time += 1
        while passengers_size > 0:
            if curr_time >= passengers[0].get_start_waiting_time():
                new_passenger = heapq.heappop(passengers)
                heapq.heappush(available_passengers, new_passenger)
                new_passenger.start_timer(curr_time)
                passengers_size -= 1
            else:
                break
        while drivers_size > 0:
            if curr_time >= float(drivers[0].get_start_time()):
                new_driver = heapq.heappop(drivers)
                available_drivers.append(new_driver)
                new_driver.start_timer(curr_time)
                drivers_size -= 1
            else:
                break

        if drivers_size == 0:
            if not available_drivers:
                # No drivers available to drive the passengers-- break.
                print("Ran out of drivers...")
                break

        # if(passengers_driven >60): # For limiting the number of passengers to drive for time
        #     break
        driver = None
        # Note that this lends itself to being parallel, so that different drivers at
        # the same time could actually get different passengers.  :s
        while (len(available_drivers) > 0):
            if (len(available_passengers) > 0):
                passenger = heapq.heappop(available_passengers)
                if not driver:
                    #IMPORTANT IF USING GOOGLE COLAB UNCOMMENT THE THING BELOW
                    #*******^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^*****
                    #driver = available_drivers[0]
                    
                    end_node = passenger.find_nearest_node(passenger.start_location)[0]
                    min_pickup_time = float('inf')
                    
                    index = -1
                    for i in range(len(available_drivers)):
                        start_node = available_drivers[i].find_nearest_node(available_drivers[i].location)
                        # print("Hours %d"% available_drivers[i].get_start_hour())
                        timeDrive = calculate_estimated_time(start_node, end_node, is_weekday_or_weekend(available_drivers[i].start_time), available_drivers[i].get_start_hour(), min_pickup_time)
                        if timeDrive < min_pickup_time:
                            min_pickup_time = timeDrive
                            # print("New driver: %f", min_pickup_time)
                            driver = available_drivers[i]
                            index = i

                if not passenger.benchmark_time_start:
                    print("Benchmark time not started!")
                    print(passenger)
                    exit()
                
                #when passanger is being picked up
                driver.start_time = curr_time + min_pickup_time 
                dropoff_node = passenger.find_nearest_node(passenger.desired_location)[0]
                drop_off_time = calculate_estimated_time(end_node, dropoff_node, is_weekday_or_weekend(driver.start_time), driver.get_start_hour(), float('inf'))
                
                if driver.drive_passenger_T3(passenger, min_pickup_time, drop_off_time, current_time = curr_time) == -1: #CHANGE/ CREATE METHOD TO BE T3 alg instead of haversine_distance
                    print("Uh oh, a done driver drove!")
                    print(driver)
                    exit()
                
                print("Passenger: %d Estimated Pickup Time: %f Estimated drop-off time %f" % (passengers_driven, min_pickup_time,drop_off_time))
                print("--- %s seconds ---" % (time.time() - start_time))

                passengers_driven += 1
                
                if driver.check_if_done_driving():
                    done_drivers.append(driver)
                    available_drivers.remove(driver)
                    
                    if driver in available_drivers:
                        print("Removal did not work. Exiting...")
                        exit()
                    
                    driver = None
                    
                else:
                    start_node  = passenger.find_nearest_node(passenger.start_location)[0] #pick up
                    end_node, dropoff_lat, dropoff_lon = passenger.find_nearest_node(passenger.desired_location) # drop off location
                    
                    # increments by the estimated time to pick up and drive passenger
                    driver.start_time += drop_off_time
                    driver.location = (dropoff_lat, dropoff_lon)

                    heapq.heappush(drivers, driver)
                    available_drivers.remove(driver)
                    drivers_size += 1
                    driver = None
                    
                done_passengers.append(passenger)
                passenger = None
            else:
                break
                    
            
        # print(f"{time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(curr_time))} | Remaining Passengers: {passengers_size}")

    print(f"Number of Drivers left: {len(available_drivers)} | Number of passengers driven: {passengers_driven}")

    # ========================================= Runtime, Statistics, and Benchmarks ==================================================
    runtime_end = time.time()

    runtime = runtime_end - runtime_start
    
    return (done_passengers, done_drivers, runtime)


if __name__ == "__main__":
    from benchmarking import run_t3
    
    run_t3()