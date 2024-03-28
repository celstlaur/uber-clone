import matplotlib.pyplot as plt
import numpy as np
import csv
import json
import time
from passengers import Passenger
from drivers import Driver
from roads import Roads
from T1 import T1
from T2 import T2
from T3 import T3
from T4 import T4
from T5 import T5

# for benchmarking, use pyplot to graph/visualize efficiency differences
# TODO: write driver function to run all Ts
# TODO: write functions to benchmark and visualize efficiency
#                                       - also driver profit/passenger wait times

ARBITRARY_BIG_NUMBER = 65536
PASSENGER_COUNT = 5002
DRIVER_COUNT = 499

BENCHMARK_T1 = True
BENCHMARK_T2 = True
BENCHMARK_T3 = True
BENCHMARK_T4 = True
BENCHMARK_T5 = True

def load_passengers():
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
            
    return passengers

# Loading in all drivers

def load_drivers():
    drivers = []
    with open("drivers.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            driver = Driver(
                time.mktime(time.strptime(row["Date/Time"], "%m/%d/%Y %H:%M:%S")),
                (float(row["Source Lat"]), float(row["Source Lon"])),
            )
            drivers.append(driver)
            
    return drivers

def load_roads():
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
                    
    return road_list
                    
def load_node_map():
    node_map = dict()
    with open("node_data.json", "r") as file:
        data = json.load(file)
        for node_id in data:
            node_struct = (data[node_id]["lat"], data[node_id]["lon"])
            # print(node_struct)
            # print("Node ID: %s \n",node_id)
            node_map[node_struct] = node_id
            
    return node_map

class DriverRecord:
    def __init__(self,
                 drove_count,
                 money_min,
                 money_max,
                 money_average,
                 drive_time_min,
                 drive_time_max,
                 drive_time_average):
        self.drove_count = drove_count
        self.money_min = money_min
        self.money_max = money_max
        self.money_average = money_average
        self.drive_time_min = drive_time_min
        self.drive_time_max = drive_time_max
        self.drive_time_average = drive_time_average
        
    def get_money_list(self):
        return [self.money_min, self.money_average, self.money_max]
    
    def get_time_list(self):
        return [self.drive_time_min, self.drive_time_average, self.drive_time_max]
        
class PassengerRecord:
    def __init__(self,
                 drove_count,
                 wait_time_min,
                 wait_time_max,
                 wait_time_average,
                 ):
        self.drove_count = drove_count
        self.wait_time_min = wait_time_min
        self.wait_time_max = wait_time_max
        self.wait_time_average = wait_time_average
        
    def get_time_list(self):
        return [self.wait_time_min, self.wait_time_average, self.wait_time_max]

def get_driver_data(done_drivers):
    money_max = -1 * ARBITRARY_BIG_NUMBER
    money_min = ARBITRARY_BIG_NUMBER

    drive_time_max = -1 * ARBITRARY_BIG_NUMBER
    drive_time_min = ARBITRARY_BIG_NUMBER

    money_total = 0
    drive_time_total = 0
    for driver in done_drivers:
        # print(driver)
        driver_money = (driver.get_ride_profit())
        money_total += driver_money
        if driver_money > money_max:
            money_max = driver_money

        elif driver_money < money_min:
            money_min = driver_money

        drive_time = driver.get_driving_time()
        drive_time_total += drive_time

        if drive_time > drive_time_max:
            drive_time_max = drive_time

        elif drive_time < drive_time_min:
            drive_time_min = drive_time

    money_average = money_total / len(done_drivers)
    drive_time_average = drive_time_total / len(done_drivers)
    
    drove_count = len(done_drivers)
    
    return DriverRecord(drove_count, money_min, money_max, money_average,
            drive_time_min, drive_time_max, drive_time_average)

def get_passenger_data(done_passengers):
    wait_max = -1 * ARBITRARY_BIG_NUMBER
    wait_min = ARBITRARY_BIG_NUMBER
    wait_total = 0
    for passenger in done_passengers:
        pass_time = (passenger.get_total_waiting_time())
        # print(f"{passenger} and wait time: {pass_time}")
        wait_total += pass_time
        if pass_time > wait_max:
            wait_max = pass_time
            continue

        if pass_time < wait_min:
            wait_min = pass_time
            continue

    wait_average = wait_total / len(done_passengers)
    
    done_passenger_count = len(done_passengers)
    
    return PassengerRecord(done_passenger_count, wait_min, 
                           wait_max, wait_average)

def benchmark_print_statement(
    runtime,
    passenger_record,
    driver_record,
):
    print(f"Algorithm took {runtime} seconds to run.")
    print(
        f"Drivers that drove: {driver_record.drove_count} | Highest driver income was {driver_record.money_max} | Lowest was {driver_record.money_min} sec | Average was {driver_record.money_average} sec"
    )
    print(
        f"Longest drive time was {driver_record.drive_time_max} | Shortest drive time was {driver_record.drive_time_min} sec | Average was {driver_record.drive_time_average} sec"
    )
    print(
        f"Passengers picked up: {passenger_record.drove_count}   | Highest passenger wait time was {passenger_record.wait_time_max} | Lowest was {passenger_record.wait_time_min} sec | Average was {passenger_record.wait_time_average} sec"
    )

    if PASSENGER_COUNT != passenger_record.drove_count:
        print(
            f"Note that not all passengers were picked up. Initial passengers: {PASSENGER_COUNT}. Final: {passenger_record.drove_count}"
        )

    if DRIVER_COUNT != driver_record.drove_count:
        print(
            f"Note that not all drivers picked up passengers. Initial drivers: {DRIVER_COUNT}. Final: {driver_record.drove_count}"
        )
        
def run_t1():

    passengers = load_passengers()
    drivers = load_drivers()
    
    t1_done_passengers, t1_done_drivers, t1_runtime = T1(passengers, drivers)

    t1_pass_data = get_passenger_data(t1_done_passengers)
    t1_drive_data = get_driver_data(t1_done_drivers)
    benchmark_print_statement(t1_runtime, t1_pass_data, t1_drive_data)
    
    return t1_pass_data, t1_drive_data, t1_runtime
    
def run_t2():

    passengers = load_passengers()
    drivers = load_drivers()
    
    done_passengers, done_drivers, runtime = T2(passengers, drivers)

    pass_data = get_passenger_data(done_passengers)
    drive_data = get_driver_data(done_drivers)
    benchmark_print_statement(runtime, pass_data, drive_data)
    
    return pass_data, drive_data, runtime

def run_t3():

    done_passengers, done_drivers, runtime = T3()

    pass_data = get_passenger_data(done_passengers)
    drive_data = get_driver_data(done_drivers)
    benchmark_print_statement(runtime, pass_data, drive_data)
    
    return pass_data, drive_data, runtime
    
def run_t4():

    done_passengers, done_drivers, runtime = T4()

    pass_data = get_passenger_data(done_passengers)
    drive_data = get_driver_data(done_drivers)
    benchmark_print_statement(runtime, pass_data, drive_data)
    
    return pass_data, drive_data, runtime

def run_t5():
    
    done_passengers, done_drivers, runtime = T5()

    pass_data = get_passenger_data(done_passengers)
    drive_data = get_driver_data(done_drivers)
    benchmark_print_statement(runtime, pass_data, drive_data)
    
    return pass_data, drive_data, runtime

def create_bar_graph(labels, values, title, label_label, value_label):
    # Check if the number of labels matches the number of values
    if len(labels) != len(values):
        raise ValueError("Number of labels must match the number of values")

    # Create a bar graph
    plt.bar(labels, values, color='blue')

    # Add labels and title
    plt.xlabel(label_label)
    plt.ylabel(value_label)
    plt.title(title)

    # Show the plot
    plt.show()


def create_multi_bar_graph(categories, values_list, title, legend_labels, label_label,  value_label):
    # Check if the number of labels matches the number of values

    colors = ["b", "g", "m", "y"]

    num_categories = len(categories)
    num_values = len(values_list[0])

    # Check if the number of legend labels matches the number of values lists
    if len(legend_labels) != num_values:
        raise ValueError("Number of legend labels must match the number of values lists")

    # Set the bar width
    bar_width = 0.2

    # Set the x positions for the bars
    x_positions = np.arange(num_categories)

    for x in range(num_values):
        # Create a bar for each set of values
        # print(x)
        vals = []
        for i in range(len(values_list)):
            vals.append(values_list[i][x])

        # print(vals)
        plt.bar(x_positions + x * bar_width, vals, width=bar_width, color=colors[x], label=legend_labels[x])

    # Add labels and title
    plt.xlabel(label_label)
    plt.ylabel(value_label)
    plt.legend()
    plt.title(title)

    # Show the plot
    plt.show()
    
def run_benchmarks():
    t1_pass_data, t1_drive_data, t1_runtime = run_t1()
    t2_pass_data, t2_drive_data, t2_runtime = run_t2()
    t3_pass_data, t3_drive_data, t3_runtime = run_t3()
    t4_pass_data, t4_drive_data, t4_runtime = run_t4()
    t5_pass_data, t5_drive_data, t5_runtime = run_t5()

    t1_pass = t1_pass_data.get_time_list()
    t1_driving = t1_drive_data.get_time_list()
    t1_driver = t1_drive_data.get_money_list()

    t2_pass = t2_pass_data.get_time_list()
    t2_driving = t2_drive_data.get_time_list()
    t2_driver = t2_drive_data.get_money_list()

    t3_pass = t3_pass_data.get_time_list()
    t3_driving = t3_drive_data.get_time_list()
    t3_driver = t3_drive_data.get_money_list()

    t4_pass = t4_pass_data.get_time_list()
    t4_driving = t4_drive_data.get_time_list()
    t4_driver = t4_drive_data.get_money_list()

    t5_pass = t5_pass_data.get_time_list()
    t5_driving = t5_drive_data.get_time_list()
    t5_driver = t5_drive_data.get_money_list()

    # # T1
    # t1_runtime = 0.21800518035888672
    # t1_avg_driver_profit = -8.75205945086858e-05
    # t1_highest_driver_profit = 0.011331488400267237
    # t1_lowest_driver_profit = -0.010773997695644119
    # t1_longest_drive = 0.10399794578552246
    # t1_shortest_drive = 0.0
    # t1_avg_drive = 0.013858557283208612
    # t1_avg_pass_waiting_time = 0.0016072665867161117
    # t1_highest_pass_waiting_time = 0.02463071497754612
    # t1_lowest_pass_waiting_time = 0.0

    # t1_pass = [t1_lowest_pass_waiting_time, t1_avg_pass_waiting_time, t1_highest_pass_waiting_time]
    # t1_driving = [t1_shortest_drive, t1_avg_drive, t1_longest_drive]
    # t1_driver = [t1_lowest_driver_profit, t1_avg_driver_profit, t1_highest_driver_profit]

    # # T2
    # # NOT SURE IF THIS IS BASED OFF THE MOST RECENT ITERATION OF T2!
    # t2_runtime = 732.9762992858887
    # t2_avg_driver_profit = 0.0024569340874282548
    # t2_highest_driver_profit = 0.03197060977619373
    # t2_lowest_driver_profit = -0.01130739517023081
    # t2_longest_drive = 220.31478071212769
    # t2_avg_drive = 33.077085973310076
    # t2_shortest_drive = 0.1419823169708252
    # t2_avg_pass_waiting_time = 4.978860687771263
    # t2_highest_pass_waiting_time = 18.573062085770445
    # t2_lowest_pass_waiting_time = 0

    # t2_pass = [t2_lowest_pass_waiting_time, t2_avg_pass_waiting_time, t2_highest_pass_waiting_time]
    # t2_driver = [t2_lowest_driver_profit, t2_avg_driver_profit, t2_highest_driver_profit]
    # t2_driving = [t2_shortest_drive, t2_avg_drive, t2_longest_drive]


    # # T3
    # # BASED OFF OF JACQUE'S RECENT INCOMPLETE RUN
    # # I EYEBALLED THE NUMBERS THEY MAY NOT BE CORRECT! i tried :)
    # t3_runtime = 5204.4453
    # t3_avg_driver_profit = 0.01088549325
    # t3_highest_driver_profit = 0.01091364
    # t3_lowest_driver_profit = -0.0000562935  # p sure this is meaningless, it was like e^5, just needs to be replaced
    # t3_shortest_drive = 0.4169
    # t3_avg_drive = 158.00 # made up this number
    # t3_longest_drive = 316.67709
    # t3_avg_pass_waiting_time = 179.1228  # approx
    # t3_highest_pass_waiting_time = 358.2456
    # t3_lowest_pass_waiting_time = 0.2333541

    # t3_pass = [t3_lowest_pass_waiting_time, t3_avg_pass_waiting_time, t3_highest_pass_waiting_time]
    # t3_driver = [t3_lowest_driver_profit, t3_avg_driver_profit, t3_highest_driver_profit]
    # t3_driving = [t3_shortest_drive, t3_avg_drive, t3_longest_drive]
    # # T4
    # t4_runtime = 920.6167478561401
    # t4_avg_driver_profit = 0.013135140153562014
    # t4_highest_driver_profit = 0.15102685207218827
    # t4_lowest_driver_profit = -0.028539507269945967
    # t4_longest_drive = 475.27554273605347
    # t4_shortest_drive = 0.011992931365966797
    # t4_avg_drive = 21.69242070050899
    # t4_avg_pass_waiting_time = 11.280640904987349
    # t4_highest_pass_waiting_time = 77.96555212402616
    # t4_lowest_pass_waiting_time = 0.0009887218475341797

    # t4_pass = [t4_lowest_pass_waiting_time, t4_avg_pass_waiting_time, t4_highest_pass_waiting_time]
    # t4_driver = [t4_lowest_driver_profit, t4_avg_driver_profit, t4_highest_driver_profit]
    # t4_driving = [t4_shortest_drive, t4_avg_drive, t4_longest_drive]

    # # T5
    # t5_runtime = 0
    # t5_avg_driver_profit = 0
    # t5_highest_driver_profit = 0
    # t5_lowest_driver_profit = 0
    # t5_shortest_drive = 0
    # t5_avg_drive = 0
    # t5_longest_drive = 0
    # t5_avg_pass_waiting_time = 0
    # t5_highest_pass_waiting_time = 0
    # t5_lowest_pass_waiting_time = 0

    # t5_pass = [t5_lowest_pass_waiting_time, t5_avg_pass_waiting_time, t5_highest_pass_waiting_time]
    # t5_driver = [t5_lowest_driver_profit, t5_avg_driver_profit, t5_highest_driver_profit]
    # t5_driving = [t5_shortest_drive, t5_avg_drive, t5_longest_drive]

    # # DATA
    t_labels = ['T1', 'T2', 'T3', 'T4', 'T5']
    runtime_efficiency = [t1_runtime, t2_runtime, t3_runtime, t4_runtime, t5_runtime]
    passenger_waiting_time = [t1_pass, t2_pass, t3_pass, t4_pass, t5_pass]
    driver_profit = [t1_driver, t2_driver, t3_driver, t4_driver, t5_driver]
    driving_time = [t1_driving, t2_driving, t3_driving, t4_driving, t5_driving]

    # Create and display efficiency bar graph
    create_bar_graph(t_labels, runtime_efficiency, "Runtime Efficiency Comparison", "Algorithms", "Runtime Efficiency")

    # Create and display passenger waiting time graph
    create_multi_bar_graph(t_labels, passenger_waiting_time, "Pass. Waiting Time Comparison",
                        ["Lowest", "Avg", "Highest"], "Algorithms", "Pass. Waiting Time")

    # Create and display passenger waiting time graph
    create_multi_bar_graph(t_labels, driver_profit, "Driver Profit Comparison",
                        ["Lowest", "Avg", "Highest"], "Algorithms", "Driver Profit")

    # Create and display driver time graph
    create_multi_bar_graph(t_labels, driving_time, "Driving Time Comparison",
                        ["Lowest", "Avg", "Highest"], "Algorithms", "Driver Profit")


if __name__ == "__main__":
    
    run_benchmarks()