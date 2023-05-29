import networkx as nx
import matplotlib
matplotlib.use('TkAgg')  #Tkinter because QT wayland wasnt working (using linux)
import matplotlib.pyplot as plt
import folium
import random

class LondonNetworkGraph:
    def __init__(self):
        self.graph = nx.DiGraph() 
        self.station = nx.DiGraph() #graph of stations
        self.connection = nx.DiGraph() #graphs of connections

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
                    display_name = data[4]
                    zone = data[5]
                    total_lines = int(data[6])
                    rail = int(data[7])

                    #Add station (equivalent to node) to graph
                    self.graph.add_node(station_id, latitude=latitude, longitude=longitude, name=name,
                                        display_name=display_name, zone=zone, total_lines=total_lines, rail=rail)
    
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
    
    def dijkstra(self, start_station, end_station): #Dijkstra's algorithm calculates the shortest path between two stations using networkx
        shortest_path = nx.dijkstra_path(self.graph, start_station, end_station)
        return shortest_path

    def visualize(self):
        # Visualização com NetworkX e Matplotlib
        position = nx.spring_layout(self.graph)
        nx.draw(self.graph, position, with_labels=True)
        plt.show()

        # Visualização com Folium
        m = folium.Map(location=[51.5074, -0.1278], zoom_start=10)

        # Adicionar marcadores para cada estação
        for station_id, station_data in self.graph.nodes(data=True):
            latitude = station_data['latitude']
            longitude = station_data['longitude']
            name = station_data['name']
            folium.Marker([latitude, longitude], popup=name).add_to(m)

        # Adicionar arestas ao mapa
        for from_station_id, to_station_id, connection_data in self.graph.edges(data=True):
            from_latitude = self.graph.nodes[from_station_id]['latitude']
            from_longitude = self.graph.nodes[from_station_id]['longitude']
            to_latitude = self.graph.nodes[to_station_id]['latitude']
            to_longitude = self.graph.nodes[to_station_id]['longitude']
            folium.PolyLine(
                locations=[(from_latitude, from_longitude), (to_latitude, to_longitude)],
                color='blue',
                weight=2,
                opacity=1
            ).add_to(m)

        # Salvar o mapa como arquivo HTML
        m.save('map.html')

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
    lng.dijkstra(40, 50)
    lng.visualize()
