#!/usr/bin/python
import RPi.GPIO as GPIO
from time import sleep
import array as arr
import random

GPIO.setmode(GPIO.BCM)
# GPIO.setmode(GPIO.BOARD)


####### SETTING UP #######

# GPIO mapping
led_0 = 10
led_3 = 9
led_6 = 11

led_1 = 23
led_4 = 24
led_7 = 25

led_2 = 16
led_5 = 20
led_8 = 21

buttonPlay = 14
buttonU = 27
buttonD = 18
buttonL = 17
buttonR = 15

# RGB player indicator
r = 26
g = 19
b = 13

push_btns = [buttonPlay, buttonU, buttonD, buttonL, buttonR]
rgb = [r, g, b]
for x in push_btns:
	GPIO.setup(x, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# index number: [GPIO pin, space status, navigation status]
# space status = 0 - blank, 1 - non-current player pieces, 2 - current player pieces
# navigation status = 1 - current position of cursor
ttt_board = [
	[led_0, 0, 0], [led_1, 0, 0], [led_2, 0, 0],
	[led_3, 0, 0], [led_4, 0, 1], [led_5, 0, 0],
	[led_6, 0, 0], [led_7, 0, 0], [led_8, 0, 0]
]
pwm_leds = []
count = 0
for x in range(0, 9):
	GPIO.setup(ttt_board[x][0], GPIO.OUT)
	pwm_leds.append(GPIO.PWM(ttt_board[x][0], 50))
	if (ttt_board[x][0] == led_4):
		pwm_leds[count].start(1)	# turn on the center led
	else:
		pwm_leds[count].start(0)	# turn everything else off
	count += 1
for color in rgb:
	GPIO.setup(color, GPIO.OUT)

duty_off = 0
duty_lo = 8
duty_hi = 100
duty_hi2 = 50

players = ['X', 'O']
player = random.choice(players)	# beginning player
winner = '' 	# initialize winning player
turn_count = 1


####### GAME PORTION #######

def printBoard():
	print("\n+---+---+---+"),
	print("\n|"),
	for space in range(0, 9):
		print(ttt_board[space][1]),
		print("|"),
		if space == 2 or space == 5:
			print("\n+---+---+---+")
			print("|"),
	print("\n+---+---+---+")
	print("Current player: " + player)
	print("Position: " + str(position))
	print("Turn: " + str(turn_count))

def gameStatus():
	# indicates if there is a winner
	if ((ttt_board[0][1] == 1 and ttt_board[0][1] == ttt_board[1][1] and ttt_board[1][1] == ttt_board[2][1]) or
		(ttt_board[3][1] == 1 and ttt_board[3][1] == ttt_board[4][1] and ttt_board[4][1] == ttt_board[5][1]) or
		(ttt_board[6][1] == 1 and ttt_board[6][1] == ttt_board[7][1] and ttt_board[7][1] == ttt_board[8][1]) or
		(ttt_board[0][1] == 1 and ttt_board[0][1] == ttt_board[3][1] and ttt_board[3][1] == ttt_board[6][1]) or
		(ttt_board[1][1] == 1 and ttt_board[1][1] == ttt_board[4][1] and ttt_board[4][1] == ttt_board[7][1]) or
		(ttt_board[2][1] == 1 and ttt_board[2][1] == ttt_board[5][1] and ttt_board[5][1] == ttt_board[8][1]) or
		(ttt_board[0][1] == 1 and ttt_board[0][1] == ttt_board[4][1] and ttt_board[4][1] == ttt_board[8][1]) or
		(ttt_board[2][1] == 1 and ttt_board[2][1] == ttt_board[4][1] and ttt_board[4][1] == ttt_board[6][1])):
		return True

def indicate_R():
	# TIE
	GPIO.output(25, True)
	GPIO.output(24, False)
	GPIO.output(23, False)

def indicate_G():
	# player X
	GPIO.output(25, False)
	GPIO.output(24, True)
	GPIO.output(23, False)

def indicate_B():
	# player O
	GPIO.output(25, False)
	GPIO.output(24, False)
	GPIO.output(23, True)
	

def swapPlayer():
	# TURN THE TABLES!!! (HAHAHA)
	print("Switching players!")
	for x in range(0, 9):
		if ttt_board[x][1] == 2:
			ttt_board[x][1] = 1
		elif ttt_board[x][1] == 1:
			ttt_board[x][1] = 2

	global player
	global winner
	if gameStatus():
		# there is a winner!
		winner = player
	else:
		if player == 'X':
			player = 'O'
		else:
			player = 'X'

	global turn_count
	turn_count += 1
	global position
	position = 4	# start new turn at center
	ttt_board[position][2] = 1
	sleep(0.1)

def buttonPressed(channel):
	global position
	if (channel == buttonPlay):
		print("CONFIRM is pressed!")
		if (ttt_board[position][1] == 0):
			ttt_board[position][1] = 2
			ttt_board[position][2] = 0
			printBoard()
			swapPlayer()
		else:
			print("... Space is already used!")
	else:
		ttt_board[position][2] = 0	# leave old cursor position
		if (channel == buttonU):
			print("UP is pressed!")
			if (position >= 3 and position <= 8):
				position = position - 3

		elif (channel == buttonD):
			print("DOWN is pressed!")
			if (position >= 0 and position <= 5):
				position = position + 3
		
		elif (channel == buttonL):
			print("LEFT is pressed!")
			if not(position == 0 or position == 3 or position == 6):
				position = position - 1

		elif (channel == buttonR):
			print("RIGHT is pressed!")
			if not(position == 2 or position == 5 or position == 8):
				position = position + 1
		ttt_board[position][2] = 1	# place cursor

	printBoard()

def resetBoard():
	global ttt_board
	ttt_board = [
		[led_0, 0, 0], [led_1, 0, 0], [led_2, 0, 0],
		[led_3, 0, 0], [led_4, 0, 1], [led_5, 0, 0],
		[led_6, 0, 0], [led_7, 0, 0], [led_8, 0, 0]
	]
	for x in range(0, 9):
		pwm_leds[x].ChangeDutyCycle(duty_off)
	
	global player
	if winner == '':
		print("Choosing random player to begin...")
		player = random.choice(players)
	else:
		player = winner
	global turn_count
	turn_count = 1

def main():
	for x in push_btns:
		GPIO.add_event_detect(x, GPIO.RISING, callback = buttonPressed, bouncetime = 300)

	while (True):
		printBoard()
		new_game = False
		sleep_time = 0.4
		while (not new_game):
			if player == 'X':
				indicate_G()
			elif player == 'O':
				indicate_B()

			for x in range(0, 9):
				# 0,0 - blank, not cursor ==> 		OFF
				# 1,0 - non-current, not-cursor ==> LOW
				# 2,0 - current, not-cursor ==> 	ON
				# 0,1 - blank, cursor ==> 			BLINK (HI <--> OFF)
				# 1,1 - non-current, cursor ==>		BLINK (HI <--> LOW)
				# 2,1 - current, cursor ==> 		BLINK lightly (HI <--> HI2)
				if ttt_board[x][1] == 0 and ttt_board[x][2] == 0:
					pwm_leds[x].ChangeDutyCycle(duty_off)
				if ttt_board[x][1] == 1 and ttt_board[x][2] == 0:
					pwm_leds[x].ChangeDutyCycle(duty_lo)
				if ttt_board[x][1] == 2 and ttt_board[x][2] == 0:
					pwm_leds[x].ChangeDutyCycle(duty_hi)
				if ttt_board[x][1] == 0 and ttt_board[x][2] == 1:
					pwm_leds[x].ChangeDutyCycle(duty_hi)
					sleep(sleep_time)
					pwm_leds[x].ChangeDutyCycle(duty_off)
				if ttt_board[x][1] == 1 and ttt_board[x][2] == 1:
					pwm_leds[x].ChangeDutyCycle(duty_hi)
					sleep(sleep_time)
					pwm_leds[x].ChangeDutyCycle(duty_lo)
				if ttt_board[x][1] == 2 and ttt_board[x][2] == 1:
					pwm_leds[x].ChangeDutyCycle(duty_hi)
					sleep(sleep_time)
					pwm_leds[x].ChangeDutyCycle(duty_hi2)
			sleep(sleep_time)
			if gameStatus():
				break
			if turn_count == 10:	# TIE
				break

		global winner
		if gameStatus():
			if winner == 'X':
				print("Player X Wins!")
				indicate_G()
				for x in range(0, 9):
					if x % 2 == 0:
						pwm_leds[x].ChangeDutyCycle(duty_hi)
					else:
						pwm_leds[x].ChangeDutyCycle(duty_off)
			elif winner == 'O':
				print("Player O Wins!")
				indicate_B()
				for x in range(0, 9):
					if x == 4:
						pwm_leds[x].ChangeDutyCycle(duty_off)
					else:
						pwm_leds[x].ChangeDutyCycle(duty_hi)
		else:
			print("TIE!!!")
			indicate_R()
			for x in range(0, 9):
				pwm_leds[x].ChangeDutyCycle(duty_hi)
			winner = ''
		
		new_game = True
		print("Starting new game!")
		sleep(5)
		resetBoard()		# begin with new game / empty board


def destroy():
	for x in range(0, 9):
		pwm_leds[x].stop()
	
	print("Cleaning up GPIO...")

if __name__ == '__main__':
	try:
		position = 4	# starting position is center
		main()			# begin game
	except KeyboardInterrupt:
		print("\n\nKeyboard interrupt!")
		destroy()
	finally:
		GPIO.cleanup()
		print("Cleaned! Thank you for playing!")
