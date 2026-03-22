import pygame
import random
from enum import Enum

class Direction(Enum):
    UP=(0,-1)
    DOWN=(0,1)
    LEFT=(-1,0)
    RIGHT=(1,0)
class gameob:
    def __init__(self,x,y,size,color)->None:
        self.x=x
        self.y=y
        self.size=size
        self.color=color
    def draw(self,screen)->None:
        pygame.draw.rect(screen,self.color,(self.x*self.size,self.y*self.size,self.size,self.size))
    def get_position(self):
        return(self.x,self.y)
class snake(gameob):
    def __init__(self,x,y,size=15)->None:
        super().__init__(x,y,size,(0,120,0))
        self.body=[(x,y)]
        self.direction=Direction.RIGHT
        self.nextdirection=Direction.RIGHT
        self.growflag=False
        self.score=0
    
    def change_direction(self,new_direction)-> None:
        opposite={
            Direction.UP:Direction.DOWN,
            Direction.DOWN:Direction.UP,
            Direction.LEFT:Direction.RIGHT,
            Direction.RIGHT:Direction.LEFT
        }
        if new_direction != opposite[self.direction]:
            self.nextdirection=new_direction
    def move(self)-> None:
        self.direction=self.nextdirection
        dx,dy=self.direction.value
        headx, heady= self.body[0]

        newhead=(headx+dx,heady+dy)
        self.body.insert(0,newhead)

        if self.growflag:
            self.growflag=False
        else:
            self.body.pop()
        self.x=newhead[0]
        self.y=newhead[1]
    def grow(self,points)-> None:
        self.growflag=True
        self.score+=points
    def hitself(self)-> bool:
        head=self.body[0]
        return head in self.body[1:]
    def hitWall(self,screen_width,screen_height)-> bool:
        headx,heady=self.body[0]
        gridwidth=screen_width//self.size
        gridheight=screen_height//self.size

        if headx<0 or headx>=gridwidth:
            return True
        if heady<0 or heady>=gridheight:
            return True
        return False
    def draw(self,screen)-> None:
        for segment in self.body[1:]:
            pygame.draw.rect(screen,self.color,(segment[0]*self.size,segment[1]*self.size,self.size,self.size))
        if self.body:
            head=self.body[0]
            pygame.draw.rect(screen,(0,200,0),(head[0]*self.size,head[1]*self.size,self.size,self.size))

    def reset(self,x,y)-> None:
        self.body=[(x,y)]
        self.direction=Direction.RIGHT
        self.nextdirection=Direction.RIGHT
        self.growflag=False
        self.score=0
        self.x=x
        self.y=y   

class food(gameob):
    def __init__(self,screen_width,screen_height,size=15)-> None:
        self.screen_width=screen_width
        self.screen_height=screen_height
        self.size=size
        self.food_color=(200,0,0)
        self.foodtype="normal"
        self.points=5
        x,y=self.random_position()
        super().__init__(x,y,size,self.food_color)
    
    def random_position(self)-> tuple:
        col=self.screen_width//self.size
        row=self.screen_height//self.size
        x=random.randint(0,col-1)
        y=random.randint(0,row-1)
        return (x,y)
    
    def respawn(self,snakebody,walls=None)-> None:
        walls=walls or []
        while True:
            self.x,self.y=self.random_position()
            if (self.x,self.y) not in snakebody and (self.x,self.y) not in walls:
                break
        
        if random.random()<0.2:
            self.foodtype="special"
            self.points=10
            self.color=(0,0,255)
        else:
            self.foodtype="normal"
            self.points=5
            self.color=(200,0,0)
    def draw(self,screen)-> None:
        centerx=self.x*self.size+self.size//2
        centery=self.y*self.size+self.size//2   
        radius=self.size//2-2
        pygame.draw.circle(screen,self.color,(centerx,centery),radius)

class wall(gameob):
    def __init__(self,x,y,size=15)-> None:
        super().__init__(x,y,size,(100,100,100))
    def draw(self,screen)-> None:
        pygame.draw.rect(screen,self.color,(self.x*self.size,self.y*self.size,self.size,self.size))

    @staticmethod
    def createBorderwall(screen_width,screen_height,size=15)-> list:
        walls=[]
        col=screen_width//size
        row=screen_height//size
        for x in range(col):
            walls.append(wall(x,0,size))
            walls.append(wall(x,row-1,size))
        for y in range(row):
            walls.append(wall(0,y,size))
            walls.append(wall(col-1,y,size))
        return walls
    @staticmethod
    def createRandomWalls(screen_width, screen_height, size=15, count=20):
        walls =[]
        positions=set()
        col=screen_width // size
        row=screen_height // size
        while len(positions) < count:
            x=random.randint(1, col - 2)
            y=random.randint(1, row - 2)
            positions.add((x, y))
        for pos in positions:
            walls.append(wall(pos[0], pos[1], size))
        return walls