import json
import time
import uuid
import urllib.parse
import os.path
from server.modules.utils import ODLRequest, generate_custom_path, generate_dijkstra_path
from server.models import Switch, Host, Link, Flow
from server.config import CONF_URL, OPERATION_URL

list_host = list()
list_switch = list()
list_links = list()


def _set_switch(node):
    node_id = node['node-id']
    node_name = 's' + node_id.split(":")[-1]
    node_link = list()
    node_flow = list()
    return Switch(node_id, node_name, node_link, node_flow)


def _set_host(node):
    host_tracker_attachment_points = node['host-tracker-service:attachment-points'][0]
    host_tracker_addresses = node['host-tracker-service:addresses'][0]
    node_ip = host_tracker_addresses['ip']
    node_id = node['node-id']
    node_name = 'h' + str(int(node_ip.split(".")[-1]))
    node_mac = host_tracker_addresses['mac']
    node_link = list()
    return Host(node_id, node_name, node_mac, node_ip, node_link)


def _set_link(links, list_host, list_switch):
    links.sort(key=lambda l: l['link-id'])
    list_link = []
    for link in links:
        node_link = Link(None, None, None, None)
        src = link['source']['source-node']
        if src.startswith('host'):
            for idx, h in enumerate(list_host):
                if h.node_id == src:
                    src_host = h
                    break
            src_index = idx
            node_link.src_id = src_host.node_id
            node_link.src_name = src_host.node_name
        else:
            for idx, s in enumerate(list_switch):
                if s.node_id == src:
                    src_switch = s
                    break
            src_index = idx
            node_link.src_id = src_switch.node_id
            node_link.src_name = src_switch.node_name
            node_link.src_port = int(link['source']['source-tp'][-1])

        dst = link['destination']['dest-node']
        if dst.startswith('host'):
            for idx, h in enumerate(list_host):
                if h.node_id == dst:
                    dst_host = h
                    break
            node_link.dst_id = dst_host.node_id
            node_link.dst_name = dst_host.node_name
        else:
            for idx, s in enumerate(list_switch):
                if s.node_id == dst:
                    dst_switch = s
                    break
            node_link.dst_id = dst_switch.node_id
            node_link.dst_name = dst_switch.node_name
            node_link.dst_port = int(link['destination']['dest-tp'][-1])
        if src.startswith('host'):
            list_host[src_index].node_link.append(node_link)
        else:
            list_switch[src_index].node_link.append(node_link)
        list_link.append(node_link)
    return list_link


def _get_node(node_info):
    if isinstance(node_info, Switch) or isinstance(node_info, Host):
        return node_info
    for switch in list_switch:
        if node_info == switch.node_id or node_info == switch.node_name:
            return switch
    for host in list_host:
        if node_info == host.node_id or node_info == host.node_name or node_info == host.node_ip or node_info == host.node_mac:
            return host
    raise Exception(
        f"Cannot find node \"{node_info}\" in list of nodes: {list_switch} {list_host}")

# API


def get_topo(forced=False):
    global list_switch, list_host, list_links
    if not forced:
        return list_switch, list_host
    list_switch = []
    list_host = []
    list_links = []
    if os.path.isfile("sdn.json"):
        with open("sdn.json", "r") as f:
            data = json.load(f)
    else:
        data = ODLRequest.get(
            OPERATION_URL + '/network-topology:network-topology')
        with open("sdn.json", "w") as f:
            json.dump(data, f, indent=4)

    topology = data['network-topology']['topology']
    if 'node' not in topology[0] or 'link' not in topology[0]:
        raise Exception(f"ERROR: Network topology is unavailable.")

    nodes = topology[0]['node']
    list_link = topology[0]['link']
    for node in nodes:
        node_id = node['node-id']
        if "openflow" in node_id:
            switch = _set_switch(node)
            list_switch.append(switch)
        else:
            host = _set_host(node)
            list_host.append(host)

    list_switch.sort(key=lambda s: int(s.node_name[1:]))
    list_host.sort(key=lambda h: int(h.node_name[1:]))

    list_links = _set_link(list_link, list_host, list_switch)
    return list_switch, list_host


def get_flow(switch):
    switch = _get_node(switch)
    url = OPERATION_URL + "/opendaylight-inventory:nodes/node/" + \
        switch.node_id + "/flow-node-inventory:table/0/"
    data = ODLRequest.get(url)
    if 'flow' not in data['flow-node-inventory:table'][0]:
        return []
    list_flow = data['flow-node-inventory:table'][0]['flow']
    node_flows = []
    for f in list_flow:
        flow_id = f['id']
        match = json.dumps(f['match']) if 'match' in f else ""
        priority = f['priority']
        if 'instructions' in f:
            actions = []
            for action in f['instructions']['instruction'][0]['apply-actions']['action']:
                action_item = dict()
                for key, value in action.items():
                    if key == 'order':
                        action_item[key] = action[key]
                    else:
                        action_item['action'] = key
                        action_item['rule'] = json.dumps(action[key])
                actions.append(action_item)
                actions.sort(key=lambda x: x['order'])
        else:
            actions = [{
                'action': "drop"
            }]

        node_flows.append({
            'flow_id': flow_id,
            'match': match,
            'actions': actions,
            'priority': priority,
        })
        node_flows.sort(key=lambda x: -x['priority'])
    return node_flows


def change_flow_id(switch):
    switch = _get_node(switch)
    url = OPERATION_URL + "/opendaylight-inventory:nodes/node/" + \
        switch.node_id + "/flow-node-inventory:table/0/"
    data = ODLRequest.get(url)
    if 'flow' not in data['flow-node-inventory:table'][0]:
        return
    list_flow = data['flow-node-inventory:table'][0]['flow']
    for idx, f in enumerate(list_flow):
        body = {"flow-node-inventory:flow": []}
        f['id'] = str(idx)
        body["flow-node-inventory:flow"].append(f)
        url = CONF_URL + "/opendaylight-inventory:nodes/node/" + switch.node_id + \
            "/flow-node-inventory:table/0/flow/" + \
            urllib.parse.quote_plus(f['id'])
        ODLRequest.put(url, body)


def _delete_flow(switch):
    switch = _get_node(switch)
    url = OPERATION_URL + "/opendaylight-inventory:nodes/node/" + \
        switch.node_id + "/table/0"
    data = ODLRequest.get(url)

    if 'flow' not in data['flow-node-inventory:table'][0]:
        return
    list_flow = data["flow-node-inventory:table"][0]['flow']
    for f in list_flow:
        url = CONF_URL + "/opendaylight-inventory:nodes/node/" + switch.node_id + \
            "/flow-node-inventory:table/0/flow/" + f['id']
        ODLRequest.delete(url)


def delete_flow(switch):
    change_flow_id(switch)
    print("Waiting 5s for ODL to update...")
    time.sleep(5)
    _delete_flow(switch)


def delete_all_flow():
    for s in list_switch:
        change_flow_id(s)
    print("Waiting 5s for ODL to update...")
    time.sleep(5)
    for s in list_switch:
        _delete_flow(s)


def add_flow(switch, protocol, inport, outport, src_mac, dst_mac):
    flow_id = "sdn_app_" + str(uuid.uuid4())[-4:]
    table_id = 0
    switch = _get_node(switch)
    switch_id = switch.node_id
    flow = Flow(flow_id, table_id, switch_id, protocol,
                inport, outport, src_mac, dst_mac)
    body = flow.as_dict()
    url = CONF_URL + "/opendaylight-inventory:nodes/node/" + \
        switch.node_id + "/flow-node-inventory:table/0/flow/" + str(flow_id)
    ODLRequest.put(url, body)


def create_flows(path, path1):
    for idx, node in enumerate(path):

        path[idx] = _get_node(node)
    first_port = 0
    second_port = 0
    for idx in range(len(path)):
        if idx == 0 or idx == len(path) - 1:
            continue
        for link in path[idx].node_link:
            if link.dst_name == path[idx - 1].node_name:
                first_port = link.src_port
            if link.dst_name == path[idx + 1].node_name:
                second_port = link.src_port

        add_flow(path[idx], 'icmp', first_port, second_port,
                 path[0].node_ip+'/32', path[-1].node_ip+'/32')
        add_flow(path[idx], 'arp', first_port, second_port,
                 path[0].node_ip+'/32', path[-1].node_ip+'/32')
        add_flow(path[idx], 'icmp', second_port, first_port,
                 path[-1].node_ip+'/32', path[0].node_ip+'/32')
        add_flow(path[idx], 'arp', second_port, first_port,
                 path[-1].node_ip+'/32', path[0].node_ip+'/32')
    for i in path1:
        if 'openflow' in i:
            # print(i)
            get_flow(i)

def route_dijkstra(nodes):
    src = _get_node(nodes[0]).node_id
    dst = _get_node(nodes[-1]).node_id
    print(src, dst)
    try:
        path = generate_dijkstra_path(
            list_links, list_switch, list_host, src, dst)
        print("\033[92mFound Path: {} \033[0m".format(path))
    except:
        raise Exception(
            "Cannot routing because all connections between switches are unavailable. Please use custom mode.")
    create_flows(list(path), path)
    # for i in path:
    #     if 'openflow' in i:
    #         # print(i)
    #         get_flow(i)
    return path


def route_custom(nodes):
    list_node = list(map(lambda x: _get_node(x), nodes))

    src = list_node[0].node_id
    dst = list_node[-1].node_id
    selected_path = []
    for node in list_node:
        if ((node != src) or (node != dst)):
            selected_path.append(node.node_id)
    try:
        path = generate_custom_path(
            list_links, list_switch, list_host, src, dst, selected_path)
    except:
        raise Exception(
            "Cannot routing because all connections between switches are unavailable.")
    create_flows(list(path), path)
    return path
