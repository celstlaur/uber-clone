#   T1.py
#
# "Consider a very simple baseline that just keeps track of
#  queues of available drivers and unmatched passengers and
#  assigns the longest waiting passenger to the first available
#  driver, whenever possible.
#  Implement this algorithm an dconduct an experiment measuring
#  the performance of the algorithm in terms of desiderata D1-D3."
#
#
#  Note that for this task, we are considering the "time" for the drivers
#  profit to be the same as the Haversine distance. The
#
# Also, in order to simulate the driver being inaccessible while driving a passenger,
# we increment the start time by a certain amount and put the driver back in the queue
# (unless the driver is done!)
#
#


import csv
from passengers import Passenger
from drivers import Driver
import time
import heapq

# ======================= Loading passengers and drivers from CSV files ==============================================

def T1(passengers, drivers):
    """
# ============================================ Actual algorithm! ============================================================
#
# This algorithm will keep going until passengers is empty or available passengers is empty.
# The only exception to this is if we run out of drivers.
#
# It works by incrementing the time on each main loop by one minute. If the starting times for any driver/passenger is less than or greater
# than the time, it gets added to the "available" queues. Then, while there are drivers in the available queue, we match the driver with the
# earliest time to the passenger who was been waiting the longest. We then increment the drivers start time and boot it back to the queue,
# unless the driver is done driving, then it is booted to the done drivers. We then get the next passenger if applicable (and also another
# driver if applicable), then rinse and repeat until finished.

"""
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
                heapq.heappush(available_drivers, new_driver)
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
        while len(available_drivers) > 0:
            # If we have available passengers, we need to match them to a driver. Else, we need to break
            # this loop and check to see if there are available passengers.
            if len(available_passengers) > 0:
                if not driver:
                    driver = available_drivers[0]
                passenger = heapq.heappop(available_passengers)
                if not passenger.benchmark_time_start:
                    print(
                        "Fatal: Benchmark time not started for this passenger! Halting algorithm."
                    )
                    print(passenger)
                    exit()

                # hour = time.localtime(curr_time).tm_hour
                # pickup_time, dropoff_time = get_travel_time(driver, passenger, hour)
                # driver.drive_passenger(passenger, pickup_time, dropoff_time)

                driver.drive_passenger(passenger, current_time = curr_time)
                passengers_driven += 1

                if driver.check_if_done_driving():
                    # print(f"Driver {total_drivers - (drivers_size + 1)} is done driving.")
                    done_drivers.append(heapq.heappop(available_drivers))
                    driver = None
                else:
                    # Increment by the time taken to drive a passenger, then put back in the queue.
                    pass_drive_time = driver.get_drivetime_for_last_passenger()
                    driver.start_time = curr_time + pass_drive_time
                    heapq.heappush(drivers, heapq.heappop(available_drivers))
                    drivers_size += 1
                    driver = None

                done_passengers.append(passenger)
            else:
                break

        # print(f"{time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(curr_time))} | Remaining Passengers: {passengers_size}")

    print(
        f"Number of Drivers left: {len(available_drivers)} | Number of passengers driven: {passengers_driven}"
    )
    
    runtime_end = time.time()
    
    runtime = runtime_end - runtime_start
    
    return (done_passengers, done_drivers, runtime)


if __name__ == "__main__":
    from benchmarking import run_t1
    
    run_t1()