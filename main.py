import pygame



pygame.init()
screen = pygame.display.set_mode((500, 700))
clock = pygame.time.Clock()

class Color:
    def __init__(self):
        self.SELECTED_TILE = (235, 216, 52)
        self.UNSELECTED_TILE = (66, 66, 66)
        self.BACKGROUND = (31, 31, 31)
        
    def generate_neighbor_color(self, neighbors):
        return (100 + neighbors * 15, 216 - neighbors * 25, 52 + neighbors*23)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"{self.x}, {self.y}"
        

class Tile:
    def __init__(self, state: bool, pos: Point):
        self.is_selected = state
        self.pos = pos
        self.coordinates = Point(0, 0) #top left
        self.side_length = 0
        self.selected_neighbors = 0
    
    def is_in_bounding_box(self, point: Point):
        return point.x >= self.coordinates.x and point.x <= self.coordinates.x + self.side_length and point.y <= self.coordinates.y + self.side_length and point.y >= self.coordinates.y
    
    def toggle_state(self):
        self.is_selected = not self.is_selected

class Matrix:
    def __init__(self, size: int):
        self.size = size
        self.matrix = [[Tile(False, Point(x, y)) for x in range(size)] for y in range(size)]
    
    def get_tile(self, point: Point):
        try:
            if point.y >= 0 and point.x >= 0:
                return self.matrix[point.y][point.x]
            else:
                return None
        except:
            return None
    
    def is_tile_selected(self, point: Point):
        return None if self.get_tile(point) == None else self.get_tile(point).is_selected


    

class InputRegister:
    def __init__(self, matrix):
        self.matrix = matrix
        self.lmb_held_down = False
        self.has_been_pressed = {}

    def get_clicked_tile(self):
        pygame.event.get()
        lmb_clicked = pygame.mouse.get_pressed()[0]
        if lmb_clicked and not self.lmb_held_down:
            self.lmb_held_down = True
            for row in self.matrix.matrix:
                for tile in row:
                    if tile.is_in_bounding_box(Point(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])):
                        return tile
        elif not lmb_clicked and self.lmb_held_down:
            self.lmb_held_down = False
        return None

    def detect_keypress(self, key, callback: object, detect_repeat=False):
        pressed_keys = pygame.key.get_pressed()
        if key not in self.has_been_pressed:
            self.has_been_pressed[key] = False
        
        if pressed_keys[pygame.K_w]:
            if not detect_repeat and self.has_been_pressed[key]:
                #Don't detect repeats
                pass
            else:
                self.has_been_pressed[key] = True
                callback()
        else:
            self.has_been_pressed[key] = False






    
class Render:
    #10 tile x 10 tile size
    def __init__(self, matrix: Matrix, screen_x: int, screen_y: int):
        self.matrix = matrix
        self.screen_height = screen_x
        self.screen_width = screen_y
        self.color = Color()

        self.tile_width = 40
        self.tile_length = 40
        self.tile_padding = 5
    
    def _draw_tile(self, tile: Tile, x: int, y: int):
        tile_rect = pygame.Rect(x, y, self.tile_width, self.tile_length)
        if tile.is_selected:
            pygame.draw.rect(screen, self.color.SELECTED_TILE, tile_rect)
        else:
            # if tile.selected_neighbors > 0:
            #     pygame.draw.rect(screen, self.color.generate_neighbor_color(tile.selected_neighbors), tile_rect)
            # else:
            pygame.draw.rect(screen, self.color.UNSELECTED_TILE, tile_rect)
    
    def assign_tile_position(self):
        board_pixel_size = self.matrix.size * (self.tile_length + self.tile_padding) - self.tile_padding
        current_x = (self.screen_width - board_pixel_size) // 2
        current_y = 435
        #last subtract tile_padding to deal with "blank space" after last tile on row is rendered
        for row in self.matrix.matrix:
            for tile in row:
                tile.coordinates = Point(current_x, current_y)
                tile.side_length = self.tile_length
                current_x += self.tile_width + self.tile_padding
            current_y -= (self.tile_length + self.tile_padding)
            current_x = (self.screen_width - board_pixel_size) // 2
        
    def update_matrix_render(self):
        board_pixel_size = self.matrix.size * (self.tile_length + self.tile_padding) - self.tile_padding
        current_x = (self.screen_width - board_pixel_size) // 2
        current_y = 435
        #last subtract tile_padding to deal with "blank space" after last tile on row is rendered
        for row in self.matrix.matrix:
            for tile in row:
                self._draw_tile(tile, current_x, current_y)
                current_x += self.tile_width + self.tile_padding
            current_y -= (self.tile_length + self.tile_padding)
            current_x = (self.screen_width - board_pixel_size) // 2

class Simulation:
    def __init__(self, matrix: Matrix):
        self.matrix = matrix
    
    def assign_cell_neighbor_amount(self):
        neighbor_calculations = [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, 1], [1, 1], [1, -1], [-1, -1]]
        for row in self.matrix.matrix:
            for tile in row:
                neighbor_count = 0
                for x_add, y_add in neighbor_calculations:
                    is_tile_selected = self.matrix.is_tile_selected(Point(tile.pos.x + x_add, tile.pos.y + y_add))
                    if is_tile_selected != None and is_tile_selected == True:
                        neighbor_count += 1
                tile.selected_neighbors = neighbor_count
                # if neighbor_count > 0:
                #     print(f"Tile pos: {tile.pos}")
                #     print(f"Tile neighbor number: {tile.selected_neighbors}")
    
    def iterate(self):
        new_matrix = self.matrix.matrix
        for row_index in range(len(self.matrix.matrix)):
            for tile_index in range(len(self.matrix.matrix[row_index])):
                if self.matrix.matrix[row_index][tile_index].selected_neighbors < 2:
                    new_matrix[row_index][tile_index].is_selected = False
                elif self.matrix.matrix[row_index][tile_index].selected_neighbors == 3:
                    new_matrix[row_index][tile_index].is_selected = True
                elif self.matrix.matrix[row_index][tile_index].selected_neighbors > 3:
                    new_matrix[row_index][tile_index].is_selected = False
                    # print(f"{tile.pos} is dead")
        self.matrix.matrix = new_matrix


                

running = True
matrix = Matrix(10)
simulation = Simulation(matrix)
render = Render(matrix, 500, 500)
input_register = InputRegister(matrix)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    tile_pressed = input_register.get_clicked_tile()
    if tile_pressed != None:
        print(tile_pressed.pos)
        tile_pressed.toggle_state()
    
    input_register.detect_keypress(pygame.K_w, simulation.iterate)
    simulation.assign_cell_neighbor_amount()


    render.update_matrix_render()
    render.assign_tile_position()
    pygame.display.flip()
    
    clock.tick(60)





        
