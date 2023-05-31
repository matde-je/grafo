import networkx as nx
import matplotlib.pyplot as plt
import folium
import random
import datetime
import math
from IPython.display import display

class LondonNetworkGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def stations(self, file_path):
        with open(file_path, 'r') as file:
            next(file)  #skip line in stations.csv (header)
            next(file)  #skip line in stations.csv (blank line)
            for line in file:
                data = line.strip().split(',')
                if len(data) == 8:
                    station_id = int(data[0])
                    latitude = float(data[1])
                    longitude = float(data[2])
                    name = data[3]
                   #display_name = data[4]  its not needed and in the csv its deformatted
                    zone = data[5]
                    total_lines = int(data[6])
                    rail = int(data[7])
                    #Add station (node) to graph
                    self.graph.add_node(station_id, latitude=latitude, longitude=longitude, name=name,
                                        zone=zone, total_lines=total_lines, rail=rail)

    def connections(self, file_path):
        with open(file_path, 'r') as file:
            next(file)
            for line in file:
                data = line.strip().split(',')
                if len(data) == 7:
                    line = int(data[0])
                    from_station_id = int(data[1])
                    to_station_id = int(data[2])
                    distance = float(data[3])
                    off_peak = float(data[4])
                    am_peak = float(data[5])
                    inter_peak = float(data[6])
                    #Add connection (edge) to graph
                    self.graph.add_edge(from_station_id, to_station_id, line=line, distance=distance,
                                off_peak=off_peak, am_peak=am_peak,
                                inter_peak=inter_peak)

    def n_stations(self):   #how many stations (nodes)
        return self.graph.number_of_nodes()
    
    def n_stations_zone(self):
        zone_count = {}
        for node in self.graph.nodes:
            if 'zone' in self.graph.nodes[node]:
                zone = self.graph.nodes[node]['zone']       #dictionary with station zone values
                zone_count[zone] = zone_count.get(zone, 0) + 1  #returns the value with the zone key in the dict or 0 if theres not that key in the dict. +1 to count the occurrences of that zone
        return zone_count

    def n_edges(self):  #number of all edges (connections)
        return self.graph.number_of_edges()

    def n_edges_line(self): #number of edges per line in london "tube" (metro)
        line_count = {}
        for connection in self.graph.edges.values():    #dictionary
            line = connection['line']   #line is an int object
            line_count[line] = line_count.get(line, 0) + 1  #returns the value with the line key in the dict or 0 if theres not that key in the dict. +1 to count the occurrences of that line
        return line_count
    
    def mean_degree(self):  #grau médio das estações = número de conexões 
        degrees = [degree for n, degree in self.graph.degree()]
        return sum(degrees) / len(degrees)

    def mean_weight(self, weight):  #peso médio das conexões (edge) (distância)
        weights = [connection[weight] for connection in self.graph.edges.values()]  #connection is a dictionary with edge values, e.g, weight (distance) data
        return sum(weights) / len(weights)
   
    def randomize_locations(self, x1, x2, y1, y2):
        start_latitude = random.uniform(x1, x2)
        start_longitude = random.uniform(y1, y2)
        end_latitude = random.uniform(x1, x2)
        end_longitude = random.uniform(y1, y2)
        start_point = (start_latitude, start_longitude) #tuple of coordinates
        end_point = (end_latitude, end_longitude)
        while start_point == end_point:
            self.randomize_locations(x1, x2, y1, y2)
        print('Start point is: ', start_point, 'End point is: ', end_point) #check values
        return start_point, end_point
    
    def randomize_time(self):
        hour = random.randint(0, 23)
        if 7 <= hour < 10:  #am peak
            start_time = 1
        elif 10 <= hour < 16:   #inter peak
            start_time = 2
        else:
            start_time = 3 #'Off Peak'
        print('Peak is:', start_time, '. Hour is:', hour)   #check values
        return start_time

    def find_nearest_station(self, point):
        min_distance = float('inf')
        nearest_station = None
        for station_id, station_data in self.graph.nodes(data=True): #(station_id, station_data) is a tuple. station_data is a dictionary
            latitude = station_data.get('latitude')
            longitude = station_data.get('longitude')
            if latitude is None or longitude is None:
                continue
            station_point = (latitude, longitude)
            distance = self.calculate_distance(point, station_point)
            if distance < min_distance:
                min_distance = distance
                nearest_station = station_id
        print('Nearest station is:', nearest_station)
        return nearest_station

    def calculate_distance(self, point1, point2):   #distancia euclidiana
        x1, y1 = point1
        x2, y2 = point2
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance

    def shortest_path(self, x1, x2, y1, y2):
        start_time = self.randomize_time()
        start_point, end_point = self.randomize_locations(x1, x2, y1, y2)
        start_station = self.find_nearest_station(start_point)
        end_station = self.find_nearest_station(end_point)
        while start_station == end_station:
            start_point, end_point = self.randomize_locations(x1, x2, y1, y2)
            start_station = self.find_nearest_station(start_point)
            end_station = self.find_nearest_station(end_point)
        if start_time == 1:
            shortest_path = nx.dijkstra_path(self.graph, start_station, end_station, weight='am_peak')  #shortest path is a list of int
        elif start_time == 2:
            shortest_path = nx.dijkstra_path(self.graph, start_station, end_station, weight='inter_peak')   
        else:
            shortest_path = nx.dijkstra_path(self.graph, start_station, end_station, weight='off_peak')
        return shortest_path


if __name__ == "__main__":
    lng = LondonNetworkGraph()
    lng.stations('stations.csv')
    lng.connections('connections.csv')
    print("Number of stations: ")
    lng.n_stations()
    print("Number of stations per zone: ")
    lng.n_stations_zone()
    print("Number of edges in graph: ")
    lng.n_edges()
    print("Number of edges, in graph, per line of the tube: ")
    lng.n_edges_line()
    print("Grau médio das estações (número de conexões): ")
    lng.mean_degree()
    print("Peso médio das conexões: ")
    lng.mean_weight('distance')
    print("Shortest path between two stations: ")
    lng.shortest_path(10, 35, -1,20)


#you can run current file in an interactive window if you're using vs code for example
