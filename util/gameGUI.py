import pygame , sys , os
import numpy as np
from pygame.locals import * 
from game import *


class CardsGame:

	def __init__(self,transcript_location,transcript_name):
		
		## create game instance
		self.transcript_name = transcript_name
		self.game = Game(os.path.join(os.path.dirname(os.path.abspath(".")),transcript_location))
		self.grid_square_length=20
		self._get_display_size()
		
		pygame.init()
		pygame.display.set_caption(transcript_name)

		self.clock = pygame.time.Clock()
		self.canvas = pygame.display.set_mode((self.DISP_WIDTH, self.DISP_HEIGHT))
		self.colors = { "BLACK":(0,0,0) , "WHITE":(255,255,255) , "RED":(255,0,0) , "BLUE":(0,0,255) , "GREEN":(0,255,0) , "GRAY":(126,126,126) }
		self.player_font = pygame.font.SysFont('Arial', 25)
		self._draw_gameboard()

		self.move_index = 0
		self.total_moves = len(self.game.all_moves)

	def _get_display_size(self):

		r,c = self.game.start_gameboard.shape
		self.DISP_WIDTH=self.grid_square_length*c
		self.DISP_HEIGHT=self.grid_square_length*r


	def _draw_gameboard(self):

		## iterate through numpy array 
		gameboard = self.game.start_gameboard
		r,c = gameboard.shape
		self.canvas.fill(self.colors[ "WHITE" ])

		#print gameboard 
		#print np.sum( gameboard )
		
		for i in range(0,r):
			for j in range(0,c):
				x,y=(j*self.grid_square_length,i*self.grid_square_length)
				entry=gameboard[i,j]
				
				if type(entry) == int:
					if entry > 0:
						pygame.draw.rect(self.canvas, self.colors[ "BLACK" ] , (x,y,self.grid_square_length,self.grid_square_length))
					elif entry < 0:
						pygame.draw.rect(self.canvas, self.colors[ "GRAY" ] , (x,y,self.grid_square_length,self.grid_square_length))
					## else, it's a white box and fill takes care of it
				else:

					if entry == "P1":
						self.p1_position = i,j
						pygame.draw.rect(self.canvas, self.colors[ "RED" ] , (x,y,self.grid_square_length,self.grid_square_length))
						self.canvas.blit(self.player_font.render('P1',True,self.colors["BLACK"]),(x,y))
					elif entry == "P2":
						self.p2_position = i,j
						pygame.draw.rect(self.canvas, self.colors[ "RED" ] , (x,y,self.grid_square_length,self.grid_square_length))
						self.canvas.blit(self.player_font.render('P2',True,self.colors["BLACK"]),(x,y))
					else: ## to implement: account for case where p1 and p2 are in the same square
						self.p1_position = i,j
						self.p2_position = i,j
						pygame.draw.rect(self.canvas, self.colors[ "RED" ] , (x,y,self.grid_square_length,self.grid_square_length))
						self.canvas.blit(self.player_font.render('B',True,self.colors["BLACK"]),(x,y))

	def render_move(self):
		print self.move_index

		move = self.game.all_moves[ self.move_index ]

		if move.move_type == "PLAYER_MOVE":
			if move.player == 1:
				i_prev,j_prev = self.p1_position
				i,j = move.coords
				self.p1_position =(i,j)

				x_prev,y_prev=j_prev*self.grid_square_length,i_prev*self.grid_square_length
				x,y=j*self.grid_square_length,i*self.grid_square_length
				
				pygame.draw.rect(self.canvas, self.colors[ "WHITE" ] , (x_prev,y_prev,self.grid_square_length,self.grid_square_length))
				pygame.draw.rect(self.canvas, self.colors[ "RED" ] , (x,y,self.grid_square_length,self.grid_square_length))
				self.canvas.blit(self.player_font.render('P1',True,self.colors["BLACK"]),(x,y))
			else:
				i_prev,j_prev = self.p2_position
				i,j = move.coords
				self.p2_position =(i,j)

				x_prev,y_prev=j_prev*self.grid_square_length,i_prev*self.grid_square_length
				x,y=j*self.grid_square_length,i*self.grid_square_length
				
				pygame.draw.rect(self.canvas, self.colors[ "WHITE" ] , (x_prev,y_prev,self.grid_square_length,self.grid_square_length))
				pygame.draw.rect(self.canvas, self.colors[ "RED" ] , (x,y,self.grid_square_length,self.grid_square_length))
				self.canvas.blit(self.player_font.render('P2',True,self.colors["BLACK"]),(x,y))

				
		print move.move_type
	
	def run(self):

		while True: # main game loop
			event = pygame.event.poll()
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if event.key == K_RIGHT:
					if self.move_index < self.total_moves - 1:
						self.move_index += 1
						self.render_move()

				elif event.key == K_LEFT:
					if self.move_index > 0:
						self.move_index -= 1
						self.render_move()


			pygame.display.update()

def main():
	g = CardsGame("data/CardsCorpus-v02/transcripts/01/cards_0000001.csv","Game 1")
	print [ move.move_type for move in g.game.all_moves[ : 10 ] ]
	g.run()



if __name__ == "__main__":
    main()