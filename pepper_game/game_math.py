import math

#normalizes a vector
def normalize(vector):
    length = math.sqrt(vector[0]**2 + vector[1]**2)
    if length == 0:
        return (0, 0)
    return (vector[0] / length, vector[1] / length)

#finds distance between two vectors
def distance(vector1, vector2):
    item1 = (vector2[0] - vector1[0]) ** 2
    item2 = (vector2[1] - vector1[1]) ** 2
    distance = math.sqrt(item1 + item2) 
    return distance

#calculates new location given a starting location, goal location, and speed
def move_towards_location(vector1, vector2, allowance, delta_time, speed):
    if distance(vector1, vector2) < allowance:
            return vector1
    direction = (vector2[0] - vector1[0], vector2[1] - vector1[1])
    direction = normalize(direction)
    move_amount = (direction[0] * delta_time * speed, direction[1] * delta_time * speed)
    new_location = (vector1[0] + move_amount[0] , vector1[1] + move_amount[1])
    return new_location

#calculates new location given a starting location, direction, and speed
def move_in_direction(vector1, direction, delta_time, speed):
    direction = normalize(direction)
    move_amount = (direction[0] * delta_time * speed, direction[1] * delta_time * speed)
    new_location = (vector1[0] + move_amount[0], vector1[1] + move_amount[1])
    return new_location

#returns if two rectangles are colliding
def is_colliding(location1, scale1, location2, scale2):
     loc1, size1 = location1, scale1
     loc2, size2 = location2, scale2
     if (loc1[0] < loc2[0] + size2[0] and
         loc1[0] + size1[0] > loc2[0] and
         loc1[1] < loc2[1] + size2[1] and
         loc1[1] + size1[1] > loc2[1]):
        return True
     return False

def is_colliding_mouse(mouse_pos, location, scale):
    if (mouse_pos[0] < location[0]  + scale[0] 
        and mouse_pos[0] > location[0]
        and mouse_pos[1] < location[1] + scale[1]
        and mouse_pos[1] > location[1]):
        return True
    return False

#returns a new location based on the collision information of two rectangles
def resolve_collision(location1, scale1, location2, scale2):
    loc1, size1 = list(location1), list(scale1)
    loc2, size2 = list(location2), list(scale2)
    overlap_x = min(loc1[0] + size1[0] - loc2[0], loc2[0] + size2[0] - loc1[0])
    overlap_y = min(loc1[1] + size1[1] - loc2[1], loc2[1] + size2[1] - loc1[1])
    
    if overlap_x < overlap_y:
        if loc1[0] < loc2[0]:
            loc1[0] -= overlap_x
        else:
            loc1[0] += overlap_x
    else:
        if loc1[1] < loc2[1]:
            loc1[1] -= overlap_y
        else:
            loc1[1] += overlap_y

    resolved_location = (loc1[0], loc1[1])
    return (resolved_location)