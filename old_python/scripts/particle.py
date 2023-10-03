class Particle:
    def __init__(self, animations, type, pos, velocity=[0, 0], frame=0):
        self.type = type
        self.animation = animations[f'particles/{type}'].copy()
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation.frame = frame
        self.animation.done = False
    
    def update(self):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.animation.update()
        return self.animation.done 
    
    def render(self, surf, offset=[0, 0]):
        img = self.animation.get_image()
        surf.blit(img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))
