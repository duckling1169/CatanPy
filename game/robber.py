class Robber():

    def __init__(self, tile_id:int):
        self.history = [[tile_id, 0]]

    def get_current_tile_id(self):
        return self.history[len(self.history)-1][0]

    def move(self, tile_id):
        self.history.append([tile_id, 0])
        return True
    
    def update(self):
        self.history[len(self.history)-1][1] = self.history[len(self.history)-1][1] + 1

