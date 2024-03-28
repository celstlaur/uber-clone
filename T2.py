import csv
from passengers import Passenger
from drivers import Driver
import time
import heapq
from distance import calculate_distance

ARBITRARY_BIG_NUMBER = 65536

def T2(passengers, drivers):
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
    passengers_driven = 0

    runtime_start = time.time()

    # Actual algorithm!
    while passengers or available_passengers:
        # We cannot just let all the passengers/drivers loose at once in the queue, so
        # we are manually incrementing the time by each minute and adding relevant
        # passengers to the queue.
        curr_time += 1
        while passengers_size > 0:
            if curr_time >= passengers[0].get_start_waiting_time():
                new_passenger = heapq.heappop(passengers)
                print(f"Popped Passenger: {new_passenger}")
                heapq.heappush(available_passengers, new_passenger)
                # print(f"Passenger at top of the queue: {available_passengers[0]}")
                new_passenger.start_timer(curr_time)
                # print(f"{available_passengers[0]} | Timer start: {available_passengers[0].benchmark_time_start}")
                passengers_size -= 1
            else:
                break
        while drivers_size > 0:
            if curr_time >= drivers[0].get_start_time():
                new_driver = heapq.heappop(drivers)
                available_drivers.append(new_driver)
                # heapq.heappush(available_drivers, new_driver)
                new_driver.start_timer(curr_time)
                drivers_size -= 1
            else:
                break

        if drivers_size == 0:
            if not available_drivers:
                # No drivers available to drive the passengers-- break.
                print("Ran out of drivers...")
                break

        driver = None
        # Note that this lends itself to being parallel, so that different drivers at
        # the same time could actually get different passengers.  :s
        while (len(available_drivers) > 0):
            if (len(available_passengers) > 0):
                passenger = heapq.heappop(available_passengers)
                if not driver:
                    #driver = available_drivers[0]
                    
                    pickup_point = passenger.find_nearest_pickup_point()

                    min_distance = ARBITRARY_BIG_NUMBER * 1.0
                    index = -1
                    for i in range(len(available_drivers)):
                        dist = calculate_distance(available_drivers[i].location, (pickup_point[1], pickup_point[2]))
                        if dist < min_distance:
                            min_distance = dist
                            driver = available_drivers[i]
                            index = i

                if not passenger.benchmark_time_start:
                    print("Benchmark time not started!")
                    print(passenger)
                    exit()
                
                if driver.drive_passenger(passenger, current_time=curr_time) == -1:
                    print("Uh oh, a done driver drove!")
                    print(driver)
                    exit()
                passengers_driven += 1
                
                if driver.check_if_done_driving():
                    # print(f"Driver {total_drivers - (drivers_size + 1)} is done driving.")
                    done_drivers.append(driver)
                    available_drivers.remove(driver)
                    # available_drivers[index] = available_drivers[-1]
                    # available_drivers.pop()
                    # available_drivers = [(priority, value) for priority, value in available_drivers if value != driver]
                    # heapq.heapify(available_drivers)
                    
                    if driver in available_drivers:
                        print("Removal did not work. Exiting...")
                        exit()
                    
                    driver = None
                    
                else:
                    # Increment by the time taken to drive a passenger, then put back in the queue.
                    pass_drive_time = driver.get_drivetime_for_last_passenger()
                    driver.start_time = curr_time + pass_drive_time
                    # heapq.heappush(drivers, heapq.heappop(available_drivers))
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
    from benchmarking import run_t2
    
    run_t2()