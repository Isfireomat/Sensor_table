import sys
import pygame
from model import * 
from defs import *
from random import randint
import queue

class Table():  
    def __init__(self):
        pygame.init()

        self.WIDTH, self.HEIGHT = 800, 600
        self.WINDOW = pygame.display.set_mode((self.WIDTH, self.HEIGHT),pygame.DOUBLEBUF,pygame.SRCALPHA)
        self.CLOCK = pygame.time.Clock()
        
        pygame.display.set_caption("Стол министра")
        
        self.colors={
            "BLACK":(0,0,0),
            "WHITE":(255,255,255),
            "RED":(255,0,0),
            "GREEN":(0,255,0),
            "BLUE":(0,0,255),
        }
        
        self.ZOOM_SPEED = 0.2
        self.MIN_ZOOM = 0.5
        self.MAX_ZOOM = 3.0
        self.scale=2

        self.FPS=144
        self.TIME_TO_MOVE=5
        self.SPEED_ANIMATION=2
        self.Timer=self.TIME_TO_MOVE*self.FPS
        
        self.camera_zoom = 1.0
        self.target_zoom = 1.0
        self.camera_offset = pygame.Vector2(0, 0)
        self.target_offset = pygame.Vector2(0, 0)

        self.slider_open = 0
        self.slider_rect = pygame.Rect(50, 200, 700, 100)
        self.scroll_x = 0
        
        self.move=False
        self.run = True

        self.cover_documents=None
        self.documents=None
        self.cover_documents_end=None
        self.documents_end=None
        self.cover_documents_frames=None
        self.documents_frames=None
        
        self.create_documents()
        self.loop()
        
    def create_documents(self):
        w,h=50,50
        pos=[(200,200),(260,200),(320,200),(200,310),(260,310)]
        # self.cover_documents=[Cover((300+((h+20)*i),300 + ((w+20)*int(i/3))),h,w,self.colors['WHITE']) for i in range(5)]
        # self.documents=[[Cover((300+((h+20)*i),300),h,w,self.colors[['RED','GREEN','BLUE'][randint(0,2)]]) for _ in range(5)] for i in range(5)]
        self.cover_documents=[Cover(pos[i],h,w,self.colors['WHITE'],randint(-5,5)) for i in range(5)]
        self.documents=[[Cover((int(pos[i][0]+randint(-5,5)),pos[i][1]+randint(-5,5)),h,w,self.colors[['RED','GREEN','BLUE'][randint(0,2)]],randint(-5,5)) for _ in range(5)] for i in range(5)]
        self.cover_documents_end=[(randint(1,self.WIDTH),randint(1,self.HEIGHT),randint(1,180)) for _ in self.cover_documents]
        self.documents_end=[[(randint(1,self.WIDTH),randint(1,self.HEIGHT),randint(1,180)) for _ in documents] for documents in self.documents]
        self.cover_documents_frames=[generate_frames(covers_documents_end,covers_documents.first_center,self.SPEED_ANIMATION,self.FPS) for covers_documents,covers_documents_end in zip(self.cover_documents,self.cover_documents_end)]
        self.documents_frames=[[generate_frames(documnet_end,documnet.first_center,self.SPEED_ANIMATION,self.FPS) for documnet,documnet_end in zip(documnets,documnets_ends)] for documnets,documnets_ends in zip(self.documents,self.documents_end)]
    
    def zoom(self):
        self.camera_zoom += (self.target_zoom - self.camera_zoom) * 0.1
        self.camera_offset += (self.target_offset - self.camera_offset) * 0.1
        width, height = self.WINDOW.get_size()
        zoom_surface = pygame.transform.scale(self.WINDOW, (int(width * self.camera_zoom), int(height * self.camera_zoom)))
        offset_x = (zoom_surface.get_width() - width) // 2 + int(self.camera_offset.x)
        offset_y = (zoom_surface.get_height() - height) // 2 + int(self.camera_offset.y)
        self.WINDOW.blit(zoom_surface, (-offset_x, -offset_y))
    
    def get_position(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        global_mouse_x = (mouse_x - self.WIDTH / 2 + self.camera_offset.x) / self.camera_zoom + self.WIDTH / 2
        global_mouse_y = (mouse_y - self.HEIGHT / 2 + self.camera_offset.y) / self.camera_zoom + self.HEIGHT / 2
        return global_mouse_x,global_mouse_y
                
    def handle_events(self):
        events=pygame.event.get()
        
        for event in events:
            # print(events)
            with open("Logs.txt", "a") as f:
                f.write(f"{event.type}\n")
            print(event.type)
            
            if event.type == pygame.QUIT:
                self.run = False
            
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.Timer>0: 
                    self.Timer=self.TIME_TO_MOVE*self.FPS
                
                if self.cover_documents_frames[0].empty() and self.Timer<0: 
                    self.cover_documents_frames=[generate_frames(covers_documents_end,covers_documents.first_center,self.SPEED_ANIMATION,self.FPS) for covers_documents,covers_documents_end in zip(self.cover_documents,self.cover_documents_end)]
                    self.documents_frames=[[generate_frames(documnet_end,documnet.first_center,self.SPEED_ANIMATION,self.FPS) for documnet,documnet_end in zip(documnets,documnets_ends)] for documnets,documnets_ends in zip(self.documents,self.documents_end)]
                    self.Timer=self.TIME_TO_MOVE*self.FPS
                
                for i,cover_document in enumerate(self.cover_documents):
                    # print(cover_document.collidepoint(self.get_position()), not self.slider_open,events, len(events)==2)
                    if cover_document.collidepoint(self.get_position()) and not self.slider_open and len(events)<=2:
                        print("+")
                        self.slider_open=i+1
                        self.start_x=0
                        self.slider_content_width=sum([e.width*self.scale for e in [cover_document]+self.documents[i]])
                        self.slider_rect.width=min(self.slider_content_width,200)
                        self.slider_rect.height=max(max([d.height*self.scale for d in self.documents[i]]),self.slider_rect.height)
                        break
                    elif self.slider_open and self.slider_rect.collidepoint(self.get_position()) :
                        self.start_x = self.get_position()[0]
                        self.move=True
                else:
                    if self.slider_open and not self.slider_rect.collidepoint(self.get_position()) and len(events)<=2: 
                        self.slider_open=0     
                    
                self.slider_rect.x=int(self.WIDTH/2-self.slider_rect.width/2)
                self.slider_rect.y=int(self.HEIGHT/2-self.slider_rect.height/2)
                    
            elif event.type==pygame.MOUSEBUTTONUP:
                self.move=False
                
            elif event.type == pygame.MOUSEMOTION and self.slider_open:
                if self.start_x and self.move:
                    dx = self.get_position()[0] - self.start_x
                    self.scroll_x = max(min(self.scroll_x + dx, 0) , self.slider_rect.width - self.slider_content_width )
                    self.start_x = self.get_position()[0]
             
            elif event.type == pygame.MOUSEWHEEL:
                if self.Timer>0:
                    self.Timer=self.TIME_TO_MOVE*self.FPS
                if event.y > 0:
                    if self.camera_zoom < self.MAX_ZOOM:
                        self.target_zoom = min(self.target_zoom + self.ZOOM_SPEED, self.MAX_ZOOM)
                elif event.y < 0:
                    if self.camera_zoom > self.MIN_ZOOM:
                        self.target_zoom = max(self.target_zoom - self.ZOOM_SPEED, self.MIN_ZOOM)
                if not self.target_zoom in [self.MAX_ZOOM,self.MIN_ZOOM]:
                    self.target_zoom = max(self.target_zoom, 1)
                    self.target_offset = pygame.Vector2(self.get_position()) - pygame.Vector2(self.WIDTH / 2, self.HEIGHT / 2)
                    self.target_offset *= (self.target_zoom - 1)
    
    def check_timer(self):
        if not self.Timer:
            if self.cover_documents_frames[0].empty(): 
                self.Timer-=1
                self.cover_documents_end=[(randint(1,self.WIDTH),randint(1,self.HEIGHT),randint(1,180)) for _ in self.cover_documents]
                self.documents_end=[[(randint(1,self.WIDTH),randint(1,self.HEIGHT),randint(1,180)) for _ in documents] for documents in self.documents]
                self.cover_documents_frames=[generate_frames(covers_documents.first_center,covers_documents_end,self.SPEED_ANIMATION,self.FPS) for covers_documents,covers_documents_end in zip(self.cover_documents,self.cover_documents_end)]
                self.documents_frames=[[generate_frames(documnet.first_center,documnet_end,self.SPEED_ANIMATION,self.FPS) for documnet,documnet_end in zip(documnets,documnets_ends)] for documnets,documnets_ends in zip(self.documents,self.documents_end)]
        elif self.Timer>=0 and not self.slider_open:
            self.Timer-=1        
    
    def draw_documents(self):
        for i, (documents, frames) in enumerate(zip(self.documents, self.documents_frames)):     
            if i+1!=self.slider_open:
                for document,frame in zip(documents,frames):
                    if not frame.empty():
                        document.move(frame.get()) 
                    document.draw(self.WINDOW)
        
        for i,(cover_documents,frame) in enumerate(zip(self.cover_documents,self.cover_documents_frames)):
            if i+1!=self.slider_open:
                if not frame.empty():
                    cover_documents.move(frame.get())
                cover_documents.draw(self.WINDOW)

    def draw_slider(self):
        if self.slider_open:
            self.WINDOW.set_clip(self.slider_rect)
            indent=0
            
            pygame.draw.rect(self.WINDOW, self.colors['WHITE'], self.slider_rect)
            for i,e in enumerate([self.cover_documents[self.slider_open-1]]+self.documents[self.slider_open-1]):
                temp_element=Cover((self.scroll_x + int(e.width*self.scale/2) + indent + self.slider_rect.x, self.slider_rect.y+int(e.height*self.scale/2),0),e.width*self.scale,e.height*self.scale,e.color)
                indent+=temp_element.width
                temp_element.draw(self.WINDOW)
            self.WINDOW.set_clip(None)
    
    def loop(self):
        while self.run:
            self.WINDOW.fill(self.colors['BLACK'])
            
            self.handle_events()
            self.check_timer()
            self.draw_documents()
            self.draw_slider()
            self.zoom()
            
            pygame.display.flip()
            self.CLOCK.tick(self.FPS)

    
if __name__=="__main__":
    Table()