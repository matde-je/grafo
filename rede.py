import networkx as nx
import matplotlib
matplotlib.use('TkAgg')  #Tkinter because QT wayland wasnt working (using linux)
import matplotlib.pyplot as plt
import folium
import random
import datetime
import math

class LondonNetworkGraph:
    def __init__(self):
        self.graph = nx.DiGraph() 

    def stations(self, file_path):
        with open(file_path, 'r') as file:
            next(file)
            next(file)
            for line in file:
                data = line.strip().split(',')
                if len(data) == 8:
                    station_id = int(data[0])
                    latitude = float(data[1])
                    longitude = float(data[2])
                    name = data[3]
                   # display_name = data[4]
                    zone = data[5]
                    total_lines = int(data[6])
                    rail = int(data[7])

                    #Add station (equivalent to node) to graph
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
                    
                    #Add connection (equivalent to edge) to graph
                    self.graph.add_edge(from_station_id, to_station_id, line=line, distance=distance,
                                off_peak=off_peak, am_peak=am_peak,
                                inter_peak=inter_peak)

    def n_stations(self):   #how many stations (nodes)
        return self.graph.number_of_nodes()
    
    def n_stations_zone(self):
        zone_count = {}
        for node in self.graph.nodes:
            if 'zone' in self.graph.nodes[node]:
                zone = self.graph.nodes[node]['zone']
                zone_count[zone] = zone_count.get(zone, 0) + 1
        return zone_count

    def n_edges(self):  #number of all edges  
        return self.graph.number_of_edges()

    def n_edges_line(self): #number of edges per line in london "tube" (metro)
        line_count = {}
        for connection in self.graph.edges.values():
            line = connection['line']
            line_count[line] = line_count.get(line, 0) + 1
        return line_count
    
    def mean_degree(self):  #grau médio das estações = número de conexões 
        degrees = [degree for _, degree in self.graph.degree()]
        return sum(degrees) / len(degrees)

    def mean_weight(self, weight):  #peso médio das conexões (arestas)
        weights = [connection[weight] for connection in self.graph.edges.values()]
        return sum(weights) / len(weights)

    # def visualize(self):
    #     # Visualização com NetworkX e Matplotlib
    #     position = nx.spring_layout(self.graph)
    #     nx.draw(self.graph, position, with_labels=True)
    #     plt.show()

    #     # Visualização com Folium
    #     m = folium.Map(location=[51.5074, -0.1278], zoom_start=10)

    #     # Adicionar marcadores para cada estação
    #     for station_id, station_data in self.graph.nodes(data=True):
    #         latitude = station_data['latitude']
    #         longitude = station_data['longitude']
    #         name = station_data['name']
    #         folium.Marker([latitude, longitude], popup=name).add_to(m)

    #     # Adicionar arestas ao mapa
    #     for from_station_id, to_station_id, connection_data in self.graph.edges(data=True):
    #         from_latitude = self.graph.nodes[from_station_id]['latitude']
    #         from_longitude = self.graph.nodes[from_station_id]['longitude']
    #         to_latitude = self.graph.nodes[to_station_id]['latitude']
    #         to_longitude = self.graph.nodes[to_station_id]['longitude']
    #         folium.PolyLine(
    #             locations=[(from_latitude, from_longitude), (to_latitude, to_longitude)],
    #             color='blue',
    #             weight=2,
    #             opacity=1
    #         ).add_to(m)

    #     # Salvar o mapa como arquivo HTML
    #     m.save('map.html')

    def randomize_locations(self, x1, x2, y1, y2):
        start_point = (random.uniform(x1, x2), random.uniform(y1, y2))
        end_point = (random.uniform(x1, x2), random.uniform(y1, y2))
        return start_point, end_point

    def randomize_time(self):
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return datetime.time(hour, minute, second)

    def find_nearest_station(self, point):
        min_distance = float('inf')
        nearest_station = None

        for station_id, station_data in self.graph.nodes(data=True):
            latitude = station_data.get('latitude')
            longitude = station_data.get('longitude')

            if latitude is None or longitude is None:
                continue

            station_point = (latitude, longitude)
            distance = self.calculate_distance(point, station_point) #this point is the start point and afterwards it is the end point

            if distance < min_distance:
                min_distance = distance
                nearest_station = station_id

        return nearest_station


    def calculate_distance(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance

    def shortest_path(self, x1, x2, y1, y2):
        start_point, end_point = self.randomize_locations(x1, x2, y1, y2)
        start_time = self.randomize_time()

        # Encontre as estações mais próximas dos pontos de partida e chegada
        start_station = self.find_nearest_station(start_point)
        end_station = self.find_nearest_station(end_point)

        # Calcule o caminho mais curto usando o algoritmo de Dijkstra do NetworkX
        shortest_path = nx.dijkstra_path(self.graph, start_station, end_station, weight=start_time)

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
  #  lng.visualize()
    
    print("Shortest path between two stations: ")
    lng.shortest_path(50, 10, 5, 200)
