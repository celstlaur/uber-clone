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

    node_map = dict()
    with open("node_data.json", "r") as file:
        data = json.load(file)
        for node_id in data:
            node_struct = (data[node_id]["lat"], data[node_id]["lon"])
            # print(node_struct)
            # print("Node ID: %s \n",node_id)
            node_map[node_struct] = node_id

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

    # find the closest node to passenger 1 in either the tree or the dict using haversine distance

    passenger_1 = passengers[0]
    min_dist = float('inf')
    closest_node = None

    dict_start = time.time()

    for key, value in node_map:
        dist = distance.haversine_distance(passenger_1.start_location[0],
                                           passenger_1.start_location[1], key, value)
        if dist < min_dist:
            min_dist = dist
            closest_node = node_map[key, value]

    dict_end = time.time() - dict_start

    print("Time to run brute force calculation:", dict_end)

    tree_start = time.time()

    closest_node_tree = search(tree_root, passenger_1.start_location)

    tree_end = time.time() - tree_start

    print("Time to run tree search:", tree_end)

    if closest_node == closest_node_tree.id:
        print("Nodes are equivalent!")
    else:
        print("Nodes are not equivalent")













