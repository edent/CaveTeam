import svgwrite
import math
import random
import base64

#	Settings
players      =   6	#	Between 1 - 6
threshold    =   3 * players
rows         =   7
columns      =  18
font_size    =  12
paper_width  = 420	# A3 Dimensions
paper_height = 297
tile_size    =  12 / math.sin(math.radians(60))

#	Fonts
font_style_score = "font-family:score"
font_style_title = "font-family:title"
font_style_slime = "font-family:slime"
font_title = "fonts/Sancreek/Sancreek_Regular_Subset.woff2"
font_slime = "fonts/Creepster/Creepster_Regular_Subset.woff2"
font_score = "fonts/Runic/Runic_Sans_Plain_Subset.woff2"

def get_vertical_offset(size):
	opposite = size * math.sin(math.radians(60))
	return 2 * opposite

def get_horizontal_offset(size):
	adjactent = size * math.cos(math.radians(60))
	return adjactent + size

def draw_hex(size, centre, colour, drawing):
	adjactent = size * math.cos(math.radians(60))
	opposite = size * math.sin(math.radians(60))
	half = size / 2.0
	top_left = (centre[0] - half, centre[1] - opposite)
	top_right = (centre[0] + half, centre[1] - opposite)
	left = (centre[0] - (half + adjactent), centre[1])
	right = (centre[0] + (half + adjactent), centre[1])
	bottom_left = (centre[0] - half, centre[1] + opposite)
	bottom_right = (centre[0] + half, centre[1] + opposite)
	
	points=[top_left, top_right, right, bottom_right, bottom_left, left]
	hex = svgwrite.shapes.Polygon(points, 
				stroke=svgwrite.rgb(0, 0, 0, '%'), 
				stroke_width=1, 
				stroke_opacity=100, 
				fill=colour, 
				fill_opacity=100)
	drawing.add(hex)

def add_score(score, centre, drawing, font):	
	score_text = svgwrite.text.Text(str(score), insert=centre, font_size=font_size, fill='black')
	score_text['text-anchor'] = 'middle'
	score_text['dy'] = font_size/3
	score_text['style'] = font
	drawing.add(score_text)

def add_victory(centre, drawing):
	exit_text = svgwrite.text.Text('EXIT', font_size=font_size/2, insert=centre, fill='black')
	exit_text['text-anchor'] = 'middle'
	exit_text['dy'] = font_size/3/2
	exit_text['style'] = font_style_title
	drawing.add(exit_text)

def add_start(centre, drawing):
	start_text = svgwrite.text.Text('START', font_size=font_size/2, insert=centre, fill='black')
	start_text['text-anchor'] = 'middle'
	start_text['dy'] = font_size/3/2
	start_text['style'] = font_style_title
	drawing.add(start_text)

def add_slime(centre, drawing):
	slime_text = svgwrite.text.Text('SLIME', font_size=font_size/2, insert=centre, fill='black')
	slime_text['text-anchor']='middle'
	slime_text['dy']=font_size/3/2
	slime_text['style'] = font_style_slime
	drawing.add(slime_text)

def get_locations_distance(pos1, pos2):
	# if we are an even number of columns away
	# then 
	if((pos1[1] - pos2[1]) % 2 == 0):
		return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
	else:
		horizontal_offset = abs(pos1[1] - pos2[1])
		# The vertical on odd rows we can either move across (and up) or across (and down)
		# for one move in either case. 
		vertical_offset = min(abs(pos1[0] - pos2[0]), abs(pos1[0] - (pos2[0] + 1)))
		return horizontal_offset + vertical_offset

def choose_starting_position():
	return (int(rows/2), 0)	

def choose_victory_position(starting_position):
	# Don't allow the victory point in the fist half of the board
	# or (if the board is _really_ small in either of the first two columns)
	min_column = max(columns/2, starting_position[0] + 2)
	column = random.randint(min_column, columns-1)
	row = random.randint(0, rows-1)
	victory_pos = (column, row)
	return victory_pos

def choose_slime_start(starting_position, victory_position):
	# Don't allow slime within three of the starting position
	min_column = starting_position[0] + 2
	column = random.randint(min_column, columns-1)
	row = random.randint(0, rows-1)
	slime_pos = (column, row)
	#	If the slime is in the same position as the exit, try again
	if (slime_pos == victory_position):
		slime_pos = choose_slime_start(starting_position, victory_position)
	return slime_pos

def get_hex_centre(row, column, size):
	offset = 0
	if column % 2 == 0:
		offset = get_vertical_offset(size) / 2.0
	return ( 
	         ((column) * get_horizontal_offset(size) + tile_size ), 
	         (offset + ((row-0.5) * get_vertical_offset(size)) )+75 )

def draw_slime_counter(drawing):
	slime_size = tile_size
	
	#	Width of tessalated hexagons 
	slime_counter_width = (slime_size * 2) + (1.5 * threshold * (slime_size))
	slime_counter_left_margin = (paper_width - slime_counter_width)/2
	
	for counter in range(0, threshold + 1):
		position = get_hex_centre(rows + 1.25, counter, slime_size)
		position = (position[0]+slime_counter_left_margin, position[1])
		draw_hex(slime_size, position, '#00FF00', drawing)
		add_score(counter, position, drawing, font_style_slime)
	
	slime_title_location = get_hex_centre(rows +0.65, -1, tile_size)
	slime_title_location = (paper_width/2, slime_title_location[1])
	slime_title_text = svgwrite.text.Text("SLIME COUNTER", insert=slime_title_location, font_size=font_size*.9, fill='green')
	slime_title_text['text-anchor'] = 'middle'
	slime_title_text['style'] = font_style_slime
	drawing.add(slime_title_text)

def add_style(drawing):
	score_font    = open(font_score, "rb").read()
	score_font_64 = "data:font/woff2;base64," + base64.b64encode(score_font).decode("ascii")
	slime_font    = open(font_slime, "rb").read()
	slime_font_64 = "data:font/woff2;base64," + base64.b64encode(slime_font).decode("ascii")
	title_font    = open(font_title, "rb").read()
	title_font_64 = "data:font/woff2;base64," + base64.b64encode(title_font).decode("ascii")
	
	css = """	@font-face {
					font-family: slime;
					src: url('"""+ slime_font_64 +"""');
				}
				@font-face {
					font-family: title;
					src: url('"""+ title_font_64 +"""');
				}
				@font-face {
					font-family: score;
					src: url('"""+ score_font_64 +"""');
				}
			"""
	drawing.defs.add(drawing.style(css))

def get_score():
	#	The rules for single and double player games are slightly different
	if players ==   1:
		return random.randint(1,  6)
	elif players == 2: 
		return random.randint(1, 12)
	else:
		return random.randint(1, threshold)

def create_board(rows, columns, size):
	#	Filename
	filename = str(players) + " player CaveTeam " + str(random.randint(100, 999)) + ".svg"
	
	#	Board size should be A3
	board = svgwrite.Drawing(filename, 
						size    = (str(paper_width)+"mm", str(paper_height)+"mm"), 
						viewBox = ('0 0 ' + str(paper_width) + ' ' + str(paper_height)) )
	#	Add fonts
	add_style(board)
	
	# Background Colour
	board.add(board.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))
		
	#	Title
	title_location = (paper_width/2,"1em") 
	title_text = svgwrite.text.Text("CaveTeam for " + str(players) + " players", 
						insert=title_location, 
						font_size=font_size*2, 
						fill='black')
	title_text['text-anchor'] = 'middle'
	title_text['style'] = font_style_title

	board.add(title_text)
	
	#	Tile positions
	starting_pos = choose_starting_position()
	victory_pos  = choose_victory_position(starting_pos)
	slime_pos    = choose_slime_start(starting_pos, victory_pos)
	
	#	Width of tessalated hexagons 
	tiles_width = (tile_size * 2) + (1.5 * (columns-1) * (tile_size))
	tiles_left_margin = (paper_width - tiles_width)/2
	
	#	Tile Background Border
	board.add(board.rect(insert=(tiles_left_margin - tile_size/2 , get_vertical_offset(size) + tile_size), 
	                     size  =(tiles_width + tile_size         , '85%'),
	                     fill  ='#e1e1e1',
	                     rx    ="5%"))


	#	Draw the tiles
	for column in range(0, columns):
		for row in range(0, rows):
			position = get_hex_centre(row, column, size)
			position = (position[0]+tiles_left_margin, position[1])

			#	Slime tile
			if (slime_pos == (column,row)):
				draw_hex(size, position, '#00FF00', board)
				add_slime(position, board)
			#	Exit tile
			elif (victory_pos == (column,row)):
				draw_hex(size, position, '#0000FF', board)
				add_victory(position, board)

			#	Starting tile
			elif(get_locations_distance((row, column), starting_pos) == 0):
				draw_hex(size, position, '#FFFF00', board)
				add_start(position, board)
			#	Tiles adjacent to the Starting Position
			elif(get_locations_distance((row, column), starting_pos) == 1):
				draw_hex(size, position, '#FFFFFF', board)
				add_score(0, position, board, font_style_score)
			#	Regular tile
			else:
				score = get_score()
				draw_hex(size, position, "#FFFFFF", board)
				add_score(score, position, board, font_style_score)

	#	Draw the Slime Counter
	draw_slime_counter(board)
	board.save()	

create_board(rows, columns, tile_size)