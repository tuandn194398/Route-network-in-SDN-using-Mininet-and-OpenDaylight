import json
import random


def auto_str(cls):

    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )
    cls.__str__ = __str__
    cls.__repr__ = __str__
    return cls

# Chứa các thông tin về switch


@auto_str
class Switch():
    def __init__(self, node_id, node_name, node_link, node_flow):
        self.node_id = node_id
        self.node_name = node_name
        self.node_link = node_link
        self.node_flow = node_flow


@auto_str
class Host():
    def __init__(self, node_id, node_name, node_mac, node_ip, node_link):
        self.node_id = node_id
        self.node_name = node_name
        self.node_mac = node_mac
        self.node_ip = node_ip
        self.node_link = node_link


@auto_str
class Link():
    def __init__(self, src_name, src_port, dst_name, dst_port):
        self.src_name = src_name
        self.src_port = src_port
        self.dst_name = dst_name
        self.dst_port = dst_port


@auto_str
class Flow():
    def __init__(self, flow_id, table_id, switch_id, protocol, inport, outport, src_mac, dst_mac):
        self.flow_id = flow_id
        self.table_id = table_id
        self.switch_id = switch_id
        self.protocol = protocol
        self.inport = inport
        self.outport = outport
        self.src_mac = src_mac
        self.dst_mac = dst_mac

    def as_dict(self):
        json_flow = {
            "flow-node-inventory:flow": [
                {
                    "id": str(self.flow_id),
                    "priority": random.randrange(100, 10000),
                    "table_id": str(self.table_id),
                    "match": {
                        # "in-port": str(self.inport),

                    },

                    "instructions": {
                        "instruction": [
                            {
                                "order": 0,
                                "apply-actions": {
                                    "action": [
                                        {
                                            "order": 0,
                                            "output-action": {
                                                "max-length": 0,
                                                "output-node-connector": str(self.outport)
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                    "idle-timeout": 0
                }
            ]
        }

        if self.protocol == 'icmp':
            match = json_flow["flow-node-inventory:flow"][0]["match"]
            match.update(
                #     {
                #     "ethernet-match": {
                #         "ethernet-source": {
                #             "address": self.src_mac,
                #         },
                #         "ethernet-destination": {
                #             "address": self.dst_mac,
                #         }
                #     }
                # },
                {"ethernet-match": {
                    "ethernet-type": {"type": 2048}},

                    "ip-match": {"ip-protocol": 1},
                    "ipv4-destination": self.dst_mac,
                 "ipv4-source": self.src_mac})
        if self.protocol == 'arp':
            match = json_flow["flow-node-inventory:flow"][0]["match"]
            match.update(
                #     {
                #     "ethernet-match": {
                #         "ethernet-source": {
                #             "address": self.src_mac,
                #         },
                #         "ethernet-destination": {
                #             "address": self.dst_mac,
                #         }
                #     }
                # },
                {"ethernet-match":
                 {"ethernet-type": {"type": 2054}},
                 "arp-source-transport-address": self.src_mac,
                 "arp-target-transport-address": self.dst_mac}
            )
        return json_flow
