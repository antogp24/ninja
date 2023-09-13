import pygame

class PhysicsEntity:
    def __init__(self, entity_type, pos, size, animations):
        self.type = entity_type 
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.flip = False
        self.animations = animations
        self.animation_offset = (-3, -3)
        self.animation_state = '' 
        self.set_animation_state('idle')
    
    def set_animation_state(self, state):
        if state != self.animation_state:
            self.animation_state = state
            self.current_animation = self.animations[f'entities/{self.type}/{self.animation_state}'].copy()

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        
        self.current_animation.update()

        if movement[0] < 0:
            self.flip = True
        elif movement[0] > 0 and self.flip:
            self.flip = False
        
    def render(self, surf, images, offset=(0, 0)):
        image = pygame.transform.flip(self.current_animation.get_image(), self.flip, False)
        pos = (self.pos[0] - offset[0] + self.animation_offset[0],
               self.pos[1] - offset[1] + self.animation_offset[1])
        surf.blit(image, pos)
        
class Player(PhysicsEntity):
    def __init__(self, pos, size, animations):
        super().__init__('player', pos, size, animations)
        self.time_in_air = 0
    
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)
        
        self.time_in_air += 1
        if self.collisions['down']:
            self.time_in_air = 0

        if self.time_in_air > 4: 
            self.set_animation_state('jump')
        elif movement[0] != 0:
            self.set_animation_state('run')
        else:
            self.set_animation_state('idle')
        