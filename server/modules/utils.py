import requests
from requests.auth import HTTPBasicAuth
import json
from urllib.parse import urljoin
from server.config import ODL_CREDS, BASE_URL

class ODLRequest:

    @staticmethod
    def _getParams(url):
        headers = {'Content-Type': 'application/json'}
        auth = HTTPBasicAuth(
            ODL_CREDS['username'], ODL_CREDS['password'])
        url = urljoin(BASE_URL, url)
        return url, headers, auth

    @staticmethod
    def _processResp(resp):
        resp.raise_for_status()
        return resp.json() if resp.text else {}

    @staticmethod
    def get(_url):
        url, headers, auth = ODLRequest._getParams(_url)
        print(f"\033[1mSending GET\033[0m {url}")
        resp = requests.get(url, headers=headers, auth=auth)
        return ODLRequest._processResp(resp)

    @staticmethod
    def put(_url, dict_obj):
        url, headers, auth = ODLRequest._getParams(_url)
        print(f"\033[1mSending PUT\033[0m {url}")
        resp = requests.put(url, json.dumps(dict_obj), headers=headers, auth=auth)
        print(json.dumps(dict_obj))
        print("\033[1mStatus code: \033[0m", resp.status_code)
        return ODLRequest._processResp(resp)

    @staticmethod
    def delete(_url):
        url, headers, auth = ODLRequest._getParams(_url)
        print(f"\033[1mSending DELETE\033[0m {url}")
        resp = requests.delete(url, headers=headers, auth=auth)
        return ODLRequest._processResp(resp)


def _dijkstra(graph, src, dst, visited=[], distances={}, predecessors={}):
    if src not in graph:
        raise Exception('The root of the shortest path tree cannot be found')
    if dst not in graph:
        raise Exception('The target of the shortest path cannot be found')
    if src == dst:
        path = []
        pred = dst
        while pred != None:
            path.append(pred)
            pred = predecessors.get(pred, None)
        return tuple(reversed(path))
    else:
        if not visited:
            distances[src] = 0
        for neighbor in graph[src]:
            if neighbor not in visited: 
                new_distance = distances[src] + graph[src][neighbor]
                if new_distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = src
        visited.append(src)
        unvisited = {}
        for k in graph:
            if k not in visited:
                unvisited[k] = distances.get(k, float('inf'))
        x = 0
        x = min(unvisited, key=unvisited.get)
        return _dijkstra(graph, x, dst, visited, distances, predecessors)

def _construct_graph(links, list_switch, list_host):
    graph = {}
    for node in list_switch:
        graph[node.node_id] = {}
    for node in list_host:
        graph[node.node_id] = {}
    for edge in links:
        graph[edge.src_id][edge.dst_id] = 1
        graph[edge.dst_id][edge.src_id] = 1
    
    return graph

def generate_dijkstra_path(links, list_switch, list_host, src, dst):
    graph = _construct_graph(links, list_switch, list_host)
    path = _dijkstra(graph, src, dst, visited=[],
                    distances={}, predecessors={})
    return path


def generate_custom_path(links, list_switch, list_host, src, dst, selected_switches):
    graph = _construct_graph(links, list_switch, list_host)
    path = []
    tmp_switches = None
    for switch in selected_switches:
        if(switch in path):
            continue
        tmp_path = _dijkstra(graph, src, switch, visited=[],
                            distances={}, predecessors={})
        for point in tmp_path:
            if (point == tmp_switches):
                continue
            path.append(point)
        src = switch
        tmp_switches = switch
    tmp_path = _dijkstra(graph, src, dst, visited=[],
                        distances={}, predecessors={})
    for point in tmp_path:
        if (point == tmp_switches):
            continue
        path.append(point)
    print(path)
    return path
