from mininet.topo import Topo
import gym
class MyTopo(Topo):
    "Simple topology example."

    def __init__(self):
        "Create custom topo."
        Topo.__init__(self)

        # Add hosts and switches
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')
        h8 = self.addHost('h8')
        h9 = self.addHost('h9')
        h10 = self.addHost('h10')

        # Them cac switch
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')
        s7 = self.addSwitch('s7')
        s8 = self.addSwitch('s8')
        s9 = self.addSwitch('s9')
        s10 = self.addSwitch('s10')

        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s3)
        self.addLink(h5, s4)
        self.addLink(h6, s6)
        self.addLink(h7, s7)
        self.addLink(h8, s9)
        self.addLink(h9, s10)
        self.addLink(h10, s10)

        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s1, s5)
        self.addLink(s2, s4)
        self.addLink(s3, s6)
        self.addLink(s4, s5)
        self.addLink(s4, s7)
        self.addLink(s5, s6)
        self.addLink(s5, s8)
        self.addLink(s6, s9)
        self.addLink(s7, s8)
        self.addLink(s7, s10)
        self.addLink(s8, s9)
        self.addLink(s8, s10)
        self.addLink(s9, s10)
        self.addLink(s1, s7)
        self.addLink(s5, s9)
        self.addLink(s3, s5)


topos = {'sdntopo': (lambda: MyTopo())}
