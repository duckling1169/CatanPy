from game.node import Point

class DisplayGrid():

    MIN_ACROSS = 21
    MIN_DOWN = 23

    def __init__(self, across, down, scale = 1, empty_icon = ' '):
        self.grid = []
        self.scale = scale
        self.empty_icon = empty_icon
        for _ in range(down):
            self.grid.append([self.empty_icon] * across)

    def get_x_scale(self):
        x_scale = []
        for i in range(65, 65 + len(self.grid[0])):
            x_scale.append(chr(i+6) if i > 65 + 25 else chr(i))
        return x_scale
    
    @staticmethod
    def convert_to_x_scale(i):
        return chr(i+6 + 65) if i  > 25 else chr(i + 65)
    
    @staticmethod
    def x_scale_convert(c):
        return ord(c)-6-65 if ord(c) > 65 + 25 else ord(c)-65
        
    def update_grid(self, icon:str, p:Point):
        self.grid[p.y][p.x] = icon

    def __str__(self):
        s = '\n'

        for i in range(len(self.grid)):
            if i > 9:
                s += str(i) + ' | '
            else:
                s += str(i) + '  | '
            
            s += ' ' * self.scale

            for j in range(len(self.grid[i])):
                curr_icon = str(self.grid[i][j])
                match len(curr_icon):
                    case 1:
                        s += curr_icon + '  '*self.scale
                    case 2:
                        s += curr_icon + ' '*self.scale
                    case 3:
                        s = s[:-1] + curr_icon + ' '*self.scale
                    case 4:
                        s = s[:-1] + curr_icon
                    case 5:
                        s = s[:-2] + curr_icon
                    case 6:
                        s = s[:-3] + curr_icon
            
            s += '\n'*self.scale

        s += '   +-'
        for i in range(len(self.grid[0])):
            s += '-+-'*self.scale

        s += '\n      '
        x_scale = self.get_x_scale()
        for c in x_scale:
            s += c + '  '*self.scale
            
        return s