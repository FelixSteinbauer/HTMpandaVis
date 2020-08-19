import os
from htm.bindings.engine_internal import Network as BaseNetwork

from pandaBaker.pandaBaker import PandaBaker
from pandaBaker.dataStructs import cDataStream

BAKE_DATABASE_FILE_PATH = os.path.join(os.getcwd(), 'bakedDatabase', 'pandaVis.db')

class Network(BaseNetwork):
    def __init__(self):
        self.firstRun = True
        self.bakePandaData = False
        self.pandaBaker = PandaBaker(BAKE_DATABASE_FILE_PATH)
        self.iteration = 0

        self.updateDataStreams = None # callback for user method
        self.dataStreams = []
        super().__init__()

    def run(self, n):
        if not self.bakePandaData:
            super().run(n)  # if not baking, just run as normal
            return

        print("Running "+str(n)+" times (iter."+str(self.iteration)+")")
        for i in range(n):
            super().run(1)
            if self.firstRun:
                self.FirstRun()

            if self.updateDataStreams is not None: # call callback to user app to fill in data to dashStreams
                self.updateDataStreams()

            self.pandaBaker.StoreIteration(self, self.iteration)

            self.iteration += 1
        self.pandaBaker.CommitBatch() # called too often? performance issue?

    def FirstRun(self):
        print("first run")
        self.firstRun = False

        structure = {}
        regions = {}
        links = {}

        structure["regions"] = regions
        structure["links"] = links

        self.pandaBaker.dataStreams = dict((name, cDataStream()) for name in self.dataStreams)  # create dicts for more comfortable code

        regionTypes = ""
        for region in self.getRegions():
            regionTypes += "," + str(region[1].getType())
            regions[region[0]] = [region[1].getType(), region[1]]

        print("There are these types of regions in the network:"+regionTypes)
        i = 0
        for l in self.getLinks():
            links[i] = [l.getSrcRegionName(), l.getSrcOutputName(), l.getDestRegionName(), l.getDestInputName()]

            i = i+1

        self.pandaBaker.PrepareDatabase(structure)

    def UpdateDataStream(self, name, value):
        self.pandaBaker.dataStreams[name].value = value



