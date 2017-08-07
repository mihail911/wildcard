import pygame , sys  os
from pygame.locals import *
from game import *
from wildcard.util.utils import Color

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
        self.colors = { "BLACK":(0,0,0) , "WHITE":(255,255,255) , "RED":(255,0,0) , "BLUE":(0,0,255) , "GREEN":(0,255,0) , "GRAY":(126,126,126) , "LIGHT-YELLOW":(255,255,153) , "LIGHT-BLUE":(135,206,250) , "CRIMSON":(220,20,60)}
        self.player_font = pygame.font.SysFont('Arial', 15)
        self.card_font = pygame.font.SysFont('Arial',17)
        self._draw_gameboard()
        self.color = Color()
        self.move_index = 0
        self.total_moves = len(self.game.all_moves)
		
    def _get_display_size(self):

        r,c = self.game.start_gameboard.shape
        self.DISP_WIDTH=self.grid_square_length*c
        self.DISP_HEIGHT=self.grid_square_length*r
	
    def _draw_gameboard(self):

		## iterate through numpy array 
		gameboard = self.game.start_gameboard
		card_positions=self.game.position_to_card

		r,c = gameboard.shape
		self.canvas.fill(self.colors[ "WHITE" ])

		for i in range(0,r):
			for j in range(0,c):
				x,y=(j*self.grid_square_length,i*self.grid_square_length)
				entry=gameboard[i,j]

				## render initial card position
				if (j,i) in card_positions:
					cards_list = card_positions[(j,i)]
					card_name = None
					
					if len( cards_list ) == 1:
						card_name = cards_list[ 0 ]
					else:
						card_name = "M" ## for "multiple cards at location"

					pygame.draw.rect(self.canvas, self.colors[ "LIGHT-YELLOW" ] , (y,x,self.grid_square_length,self.grid_square_length))
					self.canvas.blit(self.card_font.render(card_name,True,self.colors["BLACK"]),(y,x))

				if type(entry) == int:
					if entry > 0:
						pygame.draw.rect(self.canvas, self.colors[ "BLACK" ] , (x,y,self.grid_square_length,self.grid_square_length))
					elif entry < 0:
						pygame.draw.rect(self.canvas, self.colors[ "GRAY" ] , (x,y,self.grid_square_length,self.grid_square_length))
				else:
					if entry == "P1":
						self.p1_position = i,j
						pygame.draw.rect(self.canvas, self.colors[ "CRIMSON" ] , (x,y,self.grid_square_length,self.grid_square_length))
						self.canvas.blit(self.player_font.render('P1',True,self.colors["BLACK"]),(x,y))
					elif entry == "P2":
						self.p2_position = i,j
						pygame.draw.rect(self.canvas, self.colors[ "LIGHT-BLUE" ] , (x,y,self.grid_square_length,self.grid_square_length))
						self.canvas.blit(self.player_font.render('P2',True,self.colors["BLACK"]),(x,y))
					else: ## to implement: account for case where p1 and p2 are in the same square
						self.p1_position = i,j
						self.p2_position = i,j
						pygame.draw.rect(self.canvas, self.colors[ "GREEN" ] , (x,y,self.grid_square_length,self.grid_square_length))
						self.canvas.blit(self.player_font.render('B',True,self.colors["BLACK"]),(x,y))

    def render_move(self,reverse=False):

        move = self.game.all_moves[ self.move_index ]
        card_positions = self.game.position_to_card
        if move.move_type == "PLAYER_MOVE":
            print move
            if move.player == 1:
                i_prev,j_prev = self.p1_position
                i,j = move.coords
                self.p1_position =(i,j)

                x_prev,y_prev=j_prev*self.grid_square_length,i_prev*self.grid_square_length
                x,y=j*self.grid_square_length,i*self.grid_square_length

                if (i_prev,j_prev) == self.p2_position:

                    pygame.draw.rect(self.canvas, self.colors[ "LIGHT-BLUE" ] , (x_prev,y_prev,self.grid_square_length,self.grid_square_length))
                    self.canvas.blit(self.player_font.render('P2',True,self.colors["BLACK"]),(x_prev,y_prev))
             
                elif (i_prev,j_prev) in card_positions:    ## render initial card position
                    cards_list = card_positions[(i_prev,j_prev)]
                    card_name = None

                    if len( cards_list ) == 1:
                        card_name = cards_list[ 0 ]
                    else:
                        card_name = "M" ## for "multiple cards at location"

                    pygame.draw.rect(self.canvas,self.colors[ "LIGHT-YELLOW" ],(x_prev,y_prev,self.grid_square_length,self.grid_square_length))
                    self.canvas.blit(self.card_font.render(card_name,True,self.colors["BLACK"]),(x_prev,y_prev))

                else:

                    pygame.draw.rect(self.canvas, self.colors[ "WHITE" ] , (x_prev,y_prev,self.grid_square_length,self.grid_square_length))

                pygame.draw.rect(self.canvas, self.colors[ "CRIMSON" ] , (x,y,self.grid_square_length,self.grid_square_length))
                self.canvas.blit(self.player_font.render('P1',True,self.colors["BLACK"]),(x,y))
            else:
                i_prev,j_prev = self.p2_position
                i,j = move.coords
                self.p2_position =(i,j)

                x_prev,y_prev=j_prev*self.grid_square_length,i_prev*self.grid_square_length
                x,y=j*self.grid_square_length,i*self.grid_square_length

                if (i_prev,j_prev) == self.p1_position:

                    pygame.draw.rect(self.canvas, self.colors[ "CRIMSON" ] , (x_prev,y_prev,self.grid_square_length,self.grid_square_length))
                    self.canvas.blit(self.player_font.render('P1',True,self.colors["BLACK"]),(x_prev,y_prev))
               
                elif (i_prev,j_prev) in card_positions:  ## render card position
                    cards_list = card_positions[(i_prev,j_prev)]
                    card_name = None

                    if len( cards_list ) == 1:
                        card_name = cards_list[ 0 ]
                    else:
                        card_name = "M" ## for "multiple cards at location"

                    pygame.draw.rect(self.canvas,self.colors[ "LIGHT-YELLOW" ],(x_prev,y_prev,self.grid_square_length,self.grid_square_length))
                    self.canvas.blit(self.card_font.render(card_name,True,self.colors["BLACK"]),(x_prev,y_prev))

                else:

                    pygame.draw.rect(self.canvas, self.colors[ "WHITE" ] , (x_prev,y_prev,self.grid_square_length,self.grid_square_length))

                pygame.draw.rect(self.canvas, self.colors[ "LIGHT-BLUE" ] , (x,y,self.grid_square_length,self.grid_square_length))
                self.canvas.blit(self.player_font.render('P2',True,self.colors["BLACK"]),(x,y))
       
        
        elif move.move_type == "CHAT_MESSAGE_PREFIX":
            move_str = self.color.color_str("Player " + str(move.player) + " , " +
                                 move.move_type + " , " + move.message, "red")
            print move_str

        
        elif move.move_type == "PLAYER_PICKUP_CARD":
            move_str = self.color.color_str("Player " + str(move.player) + " , " +
                                 move.move_type + " , " + move.card, "yellow")

            ## update game's card dictionary (this feels somewhat ugly tbh)
            i,j=move.coords
            card=move.card
            cards_at_coords = self.game.position_to_card.get((i,j))
            if not reverse:
                if len(cards_at_coords)==1:
                    del self.game.position_to_card[(i,j)]
                    ## next time player moves from square, white rect should get rendered
                else:
                    self.game.position_to_card[(i,j)].remove(card)
            else:
                if cards_at_coords == None:
                    self.game.position_to_card[(i,j)] = [ card ]
                else:
                    self.game.position_to_card[(i,j)].append(card)

            print move_str
        
        elif move.move_type == "PLAYER_DROP_CARD":
            move_str = self.color.color_str("Player " + str(move.player) + " , " +
                                 move.move_type + " , " + move.card, "green")

            ## update game's card dictionary (this feels somewhat ugly tbh)
            i,j=move.coords
            card=move.card
            cards_at_coords = self.game.position_to_card.get((i,j))
            if not reverse:
                if cards_at_coords == None:
                    self.game.position_to_card[(i,j)] = [ card ]
                else:
                    self.game.position_to_card[(i,j)].append(card)
            else:
                if len(cards_at_coords)==1:
                    del self.game.position_to_card[(i,j)]
                    ## next time player moves from square, white rect should get rendered
                else:
                    self.game.position_to_card[(i,j)].remove(card)

            print move_str

        ## need to handle player pickup and player drop card
    def run(self):

        while True: # main game loop
            event = pygame.event.poll()
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    if self.move_index < self.total_moves - 1:
                        self.render_move()
                        self.move_index += 1

                elif event.key == K_LEFT:
                    if self.move_index > 0:
                        # TODO: Fix bug here whereby reenacting previous move isn't possible because
                        # player is at different spot on the board
                        self.move_index -= 1
                        self.render_move(reverse=True)



            pygame.display.update()

def main():
    g = CardsGame("data/CardsCorpus-v02/transcripts/01/cards_0000001.csv","Game 2")
    #print [ move.move_type for move in g.game.all_moves[ : 10 ] ]
    g.run()


if __name__ == "__main__":
    main()
