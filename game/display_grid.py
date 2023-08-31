from game.point import Point

class DisplayGrid():

    MIN_ACROSS = 25
    MIN_DOWN = 23

    def __init__(self, across:int, down:int, scale:int, empty_icon:int):
        self.grid = []
        self.scale = scale
        self.empty_icon = empty_icon
        for _ in range(down):
            self.grid.append([self.empty_icon] * across)

    def get_x_scale(self) -> [str]:
        x_scale = []
        for i in range(65, 65 + len(self.grid[0])):
            x_scale.append(chr(i+6) if i > 65 + 25 else chr(i))
        return x_scale
    
    @staticmethod
    def int_to_xscale(i) -> str:
        return chr(i+6 + 65) if i  > 25 else chr(i + 65)
    
    @staticmethod
    def xscale_to_int(c) -> int:
        return ord(c)-6-65 if ord(c) > 65 + 25 else ord(c)-65
        
    def update_grid(self, icon:str, p:Point) -> None:
        self.grid[p.y][p.x] = icon

    def __str__(self):
        s = '\n'

        for i in range(len(self.grid)-1, -1, -1):
            if i > 9:
                s += str(i) + ' |' + '  '*self.scale
            else:
                s += str(i) + '  |' + '  '*self.scale

            for j in range(len(self.grid[i])):
                curr_icon = str(self.grid[i][j])
                match len(curr_icon):
                    case 1:
                        s += curr_icon + '  '*self.scale # 2, 4
                    case 2:
                        s += curr_icon + ' ' + '  '*(self.scale-1) # 1 (1), 2 (3), 3 (5)
                    case 3:
                        s = s[:-1] + curr_icon + ' ' + '  '*(self.scale-1)
                    case 4:
                        s = s[:-1] + curr_icon + '  '*(self.scale-1)
                    case 5:
                        s = s[:-2] + curr_icon + '  '*(self.scale-1)
                    case 6:
                        s = s[:-3] + curr_icon + '  '*(self.scale-1)
            
            s += '\n'*self.scale

        s += '   +'
        for i in range(len(self.grid[0])):
            s += '--'*self.scale + '+'

        s += '\n' + ' '*4
        x_scale = self.get_x_scale()
        for c in x_scale:
            s += '  '*self.scale + c
            
        return s