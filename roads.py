import heapq


class Roads:

    def __init__(self):
        self.road_list = dict()
        self.node_neighbors = dict()

    def add_road(self, start_node, end_node, length, weekday_list, weekend_list):
        # Add the road to the road_list
        if (start_node, end_node) in self.road_list:
            print(f"Trying to add a road that already exists! | {start_node} -> {end_node}")
            return

        self.road_list[(start_node, end_node)] = [
            length,
            weekday_list,
            weekend_list,
        ]
        if start_node not in self.node_neighbors:
            self.node_neighbors[start_node] = set()

        self.node_neighbors[start_node].add(end_node)

    def exists(self, start_node, end_node):
        return (start_node, end_node) in self.road_list

    def get_neighbors(self, node):
        # Return the neighbors for the given node
        return self.node_neighbors.get(node, set())

    def get_weight(self, first_node, second_node):
        # Return the weight (length) for the road between two nodes
        return self.road_list.get((first_node, second_node), [float('inf')])[0]

    def get_road_length(self, first_node: str, second_node: str) -> float:
        """Returns the length of the road in miles.

        Args:
            first_node (str): First nodes' ID
            second_node (str): Second nodes' ID

        Returns:
            float: Length of the road
        """
        return self.road_list[(first_node, second_node)][0]

    def get_weekday_speed(self, first_node: str, second_node: str, hour: int) -> float:
        """Gets the weekday speed at a specific hour for a given road

        Note that direction between the nodes matter!

        Args:
            first_node (str): First node's ID.
            second_node (str): Second node's ID.
            hour (int): Hour we wish to get the MPH of. From 0-23.

        Returns:
            float: The MPH of the specified hour.
                    If a bad hour was inputted, returns None.
        """
        if (hour < 0 or hour > 23):
            print(f"Bad hour inputted! Hour must be integer values ranging from 0 to 23, inclusive. Inputted {hour}.")
            return None
        # for neighbor, length, weekday_list, weekend_list in self.road_list[first_node]:
        #     if neighbor == second_node:
        #         return weekday_list[hour]

        # return -1
        return self.road_list.get((first_node, second_node))[1][hour]

    def get_weekend_speed(self, first_node: str, second_node: str, hour: int) -> float:
        """Gets the weekend speed at a specific hour for a given road

        Note that direction between the nodes matter!

        Args:
            first_node (str): First node's ID
            second_node (str): Second node's ID
            hour (int): Hour we wish to get the MPH of. From 0-23.

        Returns:
            float: The MPH of the specified hour.
                    If a bad hour was inputted, returns None.
        """
        if (hour < 0 or hour > 23):
            print(f"Bad hour inputted! Hour must be integer values ranging from 0 to 23, inclusive. Inputted {hour}.")
            return None
        return self.road_list[(first_node, second_node)][2][hour]

    def get_all_node_edges(self):
        """Returns all the node edges as a list

        Returns:
            _type_: List of node edges.
        """
        return self.road_list.keys()

    def road_as_string(self, start_node: str, end_node: str) -> str:
        """Provides a string version of a given road

        Note that direction between the nodes matter!

        Args:
            start_node (str): First node of road
            end_node (str): Second node of road

        Returns:
            str: String representation of a road
        """
        return self.road_list[(start_node, end_node)].__str__()

    # def get_all_possible_roads(self, start_node, end_node):
    #         heap = [(0, [start_node])]
    #         all_paths = []

    #         while heap:
    #             (cost, path) = heapq.heappop(heap)
    #             current_node = path[-1]

    #             if current_node == end_node:
    #                 all_paths.append(path)
    #                 continue

    #             if current_node not in self.road_list:
    #                 continue

    #             for neighbor, length, _, _ in self.road_list[current_node]:
    #                 if neighbor not in path:
    #                     heapq.heappush(heap, (cost + length, path + [neighbor]))

    #         return all_paths

    # def get_all_possible_roads(self, start_node, end_node, desired_hour, day):
    #     heap = [(0, [start_node])]
    #     all_paths = []

    #     while heap:
    #         (cost, path) = heapq.heappop(heap)
    #         current_node = path[-1]

    #         if current_node == end_node:
    #             all_paths.append(path)
    #             continue

    #         if current_node not in self.road_list:
    #             continue

    #         for neighbor, length, weekday_list, weekend_list in self.road_list[current_node]:
    #             if(day == "Weekday"):
    #                 speed = self.get_weekday_speed(current_node,neighbor,desired_hour)
    #             else:
    #                 speed = self.get_weekend_speed(current_node,neighbor, desired_hour)
    #             if speed == -1:
    #                 return
    #             print(speed)
    #             #speed = self.get_speed_at_hour(weekday_list if desired_hour < 5 else weekend_list, desired_hour)
    #             time_to_travel = length / speed
    #             updated_cost = cost + time_to_travel

    #             heapq.heappush(heap, (updated_cost, path + [neighbor]))

    #     return all_paths
