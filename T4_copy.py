# implements preprocessing to efficiently find closest node to given query point
# currently implemented: node class, methods for creating/inserting nodes to 2d tree
#                        method for searching tree to find nearest neighbor
# TODO: create method to read in actual road nodes
# TODO: create (working) driver function

# modified from geeks4geeks kd tree example by Prajwal Kandekar


import distance
import csv
import heapq
import datetime
import json
from passengers import Passenger
from drivers import Driver
from roads import Roads
import time
from collections import deque
from decimal import Decimal
import heapq
from typing import List, Tuple

ARBITRARY_BIG_NUMBER = 65536

def T42():
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
                weekday_list.append(float(row[weekday]))
                weekend_list.append(float(row[weekend]))

            road_list.add_road(
                row["start_id"],
                row["end_id"],
                float(row["length"]),
                weekday_list,
                weekend_list,
            )

    # Simple node architecture for 2d tree
    class Node:
        def __init__(self, coords, idd):
            self.id = idd
            self.coords = coords
            self.left = None
            self.right = None

    # Simple driver node architecture for 2d tree
    class driverNode:
        def __init__(self, coords, idd, obj):
            self.id = idd
            self.obj = obj
            self.coords = coords
            self.left = None
            self.right = None

    NodeDict = {}
    DriverNodeDict = {}

    # Create new node w/ given coords
    def create_node(coords, nid):
        new_node = Node(coords, nid)
        NodeDict[nid] = new_node
        return new_node

    # Create new node w/ given coords
    def create_driver_node(coords, nid, driver_obj):
        new_node = driverNode(coords, nid, driver_obj)
        DriverNodeDict[nid] = new_node
        return new_node

    # Insert node to 2d tree
    # Inserts a new node and returns root of modified tree
    # The parameter depth is used to decide whether to compare X or Y coordinates
    def insert_node(root, coords, nid, depth):
        # Tree is empty: return new node as root
        if not root:
            return create_node(coords, nid)

        # Calculate current dimension of comparison
        # Just the 2 mod of depth
        cd = depth % 2

        # Compare the new point with root on current dimension 'cd'
        # and decide the left or right subtree;
        # right subtree holds all equal to or greater than root
        if coords[cd] < root.coords[cd]:
            root.left = insert_node(root.left, coords, nid, depth + 1)
        else:
            root.right = insert_node(root.right, coords, nid, depth + 1)

        # return the root of the finished tree
        return root

    # Insert node to 2d tree
    # Inserts a new node and returns root of modified tree
    # The parameter depth is used to decide whether to compare X or Y coordinates
    def insert_driver_node(root, coords, nid, depth, obj):
        # Tree is empty: return new node as root
        if not root:
            return create_driver_node(coords, nid, obj)

        # Calculate current dimension of comparison
        # Just the 2 mod of depth
        cd = depth % 2

        # Compare the new point with root on current dimension 'cd'
        # and decide the left or right subtree;
        # right subtree holds all equal to or greater than root
        if coords[cd] < root.coords[cd]:
            root.left = insert_driver_node(root.left, coords, nid, depth + 1, obj)
        else:
            root.right = insert_driver_node(root.right, coords, nid, depth + 1, obj)

        # return the root of the finished tree
        return root

    # Insert node into tree
    # Wrapper function for insert_node, just passes in depth
    def insert(root, point, nid):
        return insert_node(root, point, nid, 0)

    # Insert node into tree
    # Wrapper function for insert_node, just passes in depth
    def insert_driver(root, point, nid, obj):
        return insert_driver_node(root, point, nid, 0, obj)

    # Determine if two points are same in 2d space
    def are_points_same(point1, point2):
        # Compare individual coordinate values
        if point1[0] != point2[0] or point1[1] != point2[1]:
            return False
        else:
            return True

    # Searches for the point closest to the given point in the 2d tree
    # Parameter depth used to determine current axis
    def search_2d_tree(root, coords, depth, min_dist, curr_sol):
        # Base cases
        # If no more root, return the best found solution
        if not root:
            return curr_sol
        if are_points_same(root.coords, coords):
            return root

        # check distance from this point, compare to current minimums and update accordingly
        dist = distance.haversine_distance(coords[0], coords[1], root.coords[0], root.coords[1])
        if min_dist > dist:
            min_dist = dist
            curr_sol = root

        # Current dimension is computed using current depth and 2d dimensions
        cd = depth % 2

        # Compare point with root with respect to cd (Current dimension)
        if coords[cd] < root.coords[cd]:
            return search_2d_tree(root.left, coords, depth + 1, min_dist, curr_sol)

        return search_2d_tree(root.right, coords, depth + 1, min_dist, curr_sol)

    # Wrapper function for search_2d_tree
    # Given a point, search for the closest neighbor in the 2d tree
    def search(root, point):
        # Pass current depth as 0
        return search_2d_tree(root, point, 0, 999999999, -1)

    # CREATE 2D TREE OF NODES
    # node_count is equal to the number of nodes inserted - MAYBE UNNECESSARY?
    tree_root = None
    node_count = 0
    with open("node_data.json", "r") as file:
        data = json.load(file)
        for node_id in data:
            node_count += 1
            tree_root = insert(tree_root, [data[node_id]["lat"], data[node_id]["lon"]], node_id)

    def find_min(root, depth, axis):
        if root is None:
            return None

        next_axis = depth % 2
        if axis == next_axis:
            if root.left is None:
                return root
            return find_min(root.left, depth + 1, axis)
        else:
            left_min = find_min(root.left, depth + 1, axis)
            right_min = find_min(root.right, depth + 1, axis)

            min_node = root
            if left_min and left_min.coords[axis] < min_node.coords[axis]:
                min_node = left_min
            if right_min and right_min.coords[axis] < min_node.coords[axis]:
                min_node = right_min

            return min_node

    def delete_node(root, point, depth=0):
        if root is None:
            return None

        print(point, root)

        axis = depth % 2
        if point.coords[axis] < root.coords[axis]:
            root.left = delete_node(root.left, point, depth + 1)
        elif point.coords[axis] > root.coords[axis]:
            root.right = delete_node(root.right, point, depth + 1)
        else:
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left

            # Node with two children: Get the inorder successor (smallest
            # in the right subtree)
            temp = find_min(root.right, depth + 1, axis)

            # Copy the inorder successor's content to this node
            root.coords = temp.coords

            # Delete the inorder successor
            root.right = delete_node(root.right, temp, depth + 1)

        return root

    # slightly modified code from other files in project
    def is_weekday_or_weekend(date):
        # Get the weekday index (Monday is 0, Sunday is 6)
        weekday_index = date.weekday()

        # Check if it's a weekday (Monday to Friday)
        if 0 <= weekday_index <= 4:
            return 'Weekday'
        else:
            return 'Weekend'

    def get_edge_weight(start_node: str, end_node: str, start_time) -> float:
        """Get the edge weight (travel time) between two nodes for a specific hour.

        Args:
            start_node (str): Start node's ID.
            end_node (str): End node's ID.
            hour (int): Hour of the day (0-23).

        Returns:
            float: Edge weight (travel time) between the nodes for the given hour.
        """
        # DETERMINE WHETHER TO CALL WEEKDAY SPEED OR WEEKEND SPEED
        dt = datetime.datetime.fromtimestamp(start_time)
        length = road_list.get_road_length(start_node, end_node)

        if is_weekday_or_weekend(dt) == 'Weekday':
            speed = road_list.get_weekday_speed(start_node, end_node, hour=dt.hour)
            # print("Weekday")
        else:
            speed = road_list.get_weekend_speed(start_node, end_node, hour=dt.hour)
            # print("Weekend")
        # print("LENGTH %f"%length)
        # print("speed %f"% speed)
        # print("Time %f"%(length/speed))

        # length/speed= hrs it takes to drive their
        return (length / speed) * 60

    def heuristic(start, goal):
        # start is a node id
        start = NodeDict[start]
        # need get coords based on id
        return distance.haversine_distance(start.coords[0], start.coords[1], goal.coords[0], goal.coords[1])

    # MY Algorithm
    def astar_est_time(start_node, end_node, start_time, curr_best) -> float:
        """Calculate the estimated time for the driver to reach the passenger.

        Returns:
            float: Estimated time for the driver to reach the passenger.
        """
        if start_node is None or end_node is None:
            print("Invalid start or end node.")
            return float('inf')  # Return infinity if nodes are not valid.

        # A STAR algorithm to find the shortest path
        # Just dijkstra's + heuristic
        min_time_to_node = {}  # Initialize an empty dictionary
        min_time_to_node[start_node] = 0  # Current time serves as the starting time

        # heuristic, arrival_time, node
        priority_queue = [(0, 0, start_node)]
        visited_nodes = set()

        while priority_queue:
            priority_time, current_time, current_node = heapq.heappop(priority_queue)

            if current_node.id in visited_nodes:
                continue
            visited_nodes.add(current_node.id)

            # print(end_node, end_node.id)

            if current_node.id == end_node.id:
                # Found the shortest path to the destination node
                return min_time_to_node[current_node]

            # Explore neighbors dynamically
            for neighbor_node in road_list.get_neighbors(current_node.id):
                if neighbor_node in visited_nodes:
                    continue

                edge_weight = get_edge_weight(current_node.id, neighbor_node,
                                              start_time)  # when driver is picking up passenger

                # print(edge_weight)
                # TODO: should the edge weight be calculated based off of current time as opposed to start_time?

                if edge_weight is not None:
                    # Calculate the arrival time at the neighbor node
                    arrival_time = current_time + edge_weight

                    neigh = NodeDict[neighbor_node]
                    # Update the minimum time to reach the neighbor node
                    if neigh not in min_time_to_node or arrival_time < min_time_to_node[neigh]:
                        # print(neighbor_node)
                        min_time_to_node[neigh] = arrival_time
                        heapq.heappush(priority_queue,
                                       (arrival_time + heuristic(neighbor_node, end_node), arrival_time, neigh))

        return float('inf')  # Return infinity if no path is found

    heapq.heapify(drivers)
    heapq.heapify(passengers)

    # Create data structures in use of the algorithm.
    available_drivers = []
    available_passengers = []

    done_drivers = []
    done_passengers = []

    drivers_size = len(drivers)
    passengers_size = len(passengers)

    print(f"Number of drivers in total: {drivers_size}")
    print(f"Number of passengers in total: {passengers_size}")

    curr_time = passengers[0].get_start_waiting_time()
    # print(curr_time, type(curr_time))
    passengers_driven = 0

    runtime_start = time.time()
    start_time = time.time()

    avail_drivers = 0
    avail_drivers_tree = None

    while passengers or available_passengers:
        # We cannot just let all the passengers/drivers loose at once in the queue, so
        # we are manually incrementing the time by each minute and adding relevant
        # passengers to the queue.
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
                # print("APPENDING")
                new_driver.start_timer(curr_time)
                drivers_size -= 1
            else:
                break

        if drivers_size == 0:
            if len(available_drivers) == 0:
                # No drivers available to drive the passengers-- break.
                print("Ran out of drivers...")
                break

        driver = None
        # Note that this lends itself to being parallel, so that different drivers at
        # the same time could actually get different passengers.  :s
        while len(available_drivers) > 0:
            if len(available_passengers) > 0:
                passenger = heapq.heappop(available_passengers)
                avail_drivers_tree = None
                for drive in available_drivers:
                    new = search(tree_root, drive.location)
                    avail_drivers_tree = insert_driver(avail_drivers_tree, new.coords, new.id, drive)
                if not driver:
                    # IMPORTANT IF USING GOOGLE COLAB UNCOMMENT THE THING BELOW
                    # *******^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^*****
                    # driver = available_drivers[0]

                    end_node = search(tree_root, passenger.start_location)

                    # WE ARE PRIORITIZING THE CLOSEST DRIVER TO THE PASSENGER
                    # instead of setting min_pickup_time to infinity to start, we are setting it to the
                    # estimated time to pickup from the closest driver
                    #min_pickup_time = astar_est_time(driver_node, end_node, driver.start_time, float('inf'))
                    min_pickup_time = float('inf')

                    for i in range(len(available_drivers)):



                        # start node is the closest node in the network to the driver location
                        start_node = search(tree_root, available_drivers[i].location)

                        # print("Hours %d"% available_drivers[i].get_start_hour())

                        # timeDrive is the est time to pickup the passenger
                        timeDrive = astar_est_time(start_node, end_node, available_drivers[i].start_time,
                                                   min_pickup_time)

                        # if it is less than the previous min pickup time, replace the best driver
                        # more efficient driver/passenger pairing found!

                        # print(timeDrive, min_pickup_time)

                        if timeDrive < min_pickup_time:
                            min_pickup_time = timeDrive
                            # print("New driver: %f", min_pickup_time)

                            # very often this statement won't be triggered at all! but when it does we can get a sense
                            # of the number of drivers being iterated through
                            # print("Replacing closest driver!", len(available_drivers))

                            # replace driver
                            driver = available_drivers[i]
                            driver_node = search(avail_drivers_tree, driver.location)
                            index = i

                if not passenger.benchmark_time_start:
                    print("Benchmark time not started!")
                    print(passenger)
                    exit()

                # use 2d tree to find closest nodes to passenger location and passenger desired location

                start_node = search(tree_root, passenger.start_location)  # pick up
                end_node = search(tree_root,
                                  passenger.desired_location)  # drop off location

                # calc estimated time to drop off passenger
                drop_off_time = astar_est_time(start_node, end_node, driver.start_time, float('inf'))

                if driver.drive_passenger_T3(passenger, min_pickup_time,
                                             drop_off_time,
                                             current_time=curr_time) == -1:  # CHANGE/ CREATE METHOD TO BE T3 alg instead of haversine_distance
                    print("Uh oh, a done driver drove!")
                    print(driver)
                    exit()

                print("Passenger: %d Estimated Time: %f " % (passengers_driven, min_pickup_time))
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

                    # increments by the estimated time to pick up and drive passenger
                    driver.start_time = curr_time + min_pickup_time + drop_off_time
                    driver.location = end_node.coords
                    driver.coords = end_node.coords

                    heapq.heappush(drivers, driver)
                    # print("removing pt 2", driver)
                    available_drivers.remove(driver)
                    drivers_size += 1
                    driver = None

                done_passengers.append(passenger)
                passenger = None
            else:
                break

        # print(f"{time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(curr_time))} | Remaining Passengers: {passengers_size}")

    print(f"Number of Drivers left: {len(available_drivers)} | Number of passengers driven: {passengers_driven}")

    runtime_end = time.time()

    runtime = runtime_end - runtime_start

    return (done_passengers, done_drivers, runtime)


if __name__ == "__main__":
    T42()