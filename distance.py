# distance.py
#
# Contains helper files related to calculating the distance
# between longitude/latitude points.

from math import sin, cos, radians, sqrt, atan2


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the distance between latitude/longitude pairs
       using the Haversine formula.

       Courtesy of ChatGPT!

    Args:
        lat1 (float): Latitude of point 1
        lon1 (float): Longitude of point 1
        lat2 (float): Latitude of point 2
        lon2 (float): Longitude of point 2

    Returns:
        float: Distance between the pairs
    """
    # Radius of the Earth in miles
    R = 3956

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Calculate the differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula to calculate the distance
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance in kilometers
    distance = R * c

    return distance


def calculate_distance(
    start_location: [float, float], end_location: [float, float]
) -> float:
    """Calculates the distance between two latitude/longitude pairs

    Args:
        start_location (tuple[float, float]): Latitude/Longitude pair 1
        end_location (tuple[float, float]): Latitude/Longitude pair 2

    Returns:
        float: Calculated distance
    """
    return haversine_distance(
        start_location[0],
        start_location[1],
        end_location[0],
        end_location[1],
    )

def convert_distance_to_minutes(
    distance : float,
    mph : float,
) -> float:
    speed_in_hours = (distance/mph)
    speed_in_minutes = speed_in_hours /  60
    
    return speed_in_minutes

def convert_distance_to_seconds(
    distance : float,
    mph : float,
) -> float:
    speed_in_seconds = convert_distance_to_minutes(distance, mph) / 60
    return speed_in_seconds