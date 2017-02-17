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
		self._draw_gameboard()

	def _get_display_size(self):

		r,c = self.game.start_gameboard.shape
		self.DISP_WIDTH=self.grid_square_length*c
		self.DISP_HEIGHT=self.grid_square_length*r


	def _draw_gameboard(self):

		## iterate through numpy array 
		gameboard = self.game.start_gameboard
		r,c = gameboard.shape

		self.canvas.fill(self.colors[ "WHITE" ])

		print gameboard 
		#print np.sum( gameboard )
		
		for i in range(0,r):
			for j in range(0,c):
				x,y=(j*self.grid_square_length,i*self.grid_square_length)
				if gameboard[i,j] > 0:
					pygame.draw.rect(self.canvas, self.colors[ "BLACK" ] , (x,y,self.grid_square_length,self.grid_square_length))
				elif gameboard[i,j] < 0:
					pygame.draw.rect(self.canvas, self.colors[ "GRAY" ] , (x,y,self.grid_square_length,self.grid_square_length) )

	
	def run(self):

		while True: # main game loop
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
			pygame.display.update()


def main():
	g = CardsGame("data/CardsCorpus-v02/transcripts/01/cards_0000001.csv","Game 1")
	g.run()

if __name__ == "__main__":
    main()