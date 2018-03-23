#!/usr/bin/env python

import numpy as np
import time
import sys
#from env.environment import environment
from env.env_ import env_ui as environment
from agent.agent_ddqn import DQNAgent
from agent.agent_ddqn import EPISODES, EPISODE_LENGTH, BATCH_SIZE
import matplotlib.pyplot as plt
from collections import deque
import os.path

fds_origin_loc = []

def load_character(character_path):
	if os.path.exists(character_path):
		with open(character_path, 'r') as f:
			for content in f.readlines():
				if -1 == content.find('{'):
					continue
				content = content.split('{')[1]
				content = content.split('}')[0]
				content = content.split(',')

				loc = []
				for n in range(len(content)):
					value = int(content[n], 16)
					for b in range(8):
						if (value & (1 << b)) :
							loc.append(environment.Loc(x = b + 1, y = n))
				fds_origin_loc.append([loc, 9, len(content) - 3])

def main():

	enable_plot = True

	if enable_plot:
	    fig, ax = plt.subplots()
	    fig.show()
	    fig.canvas.draw()
	    steps = deque(maxlen=200)
	    episodes = deque(maxlen=200)
	    rewards = deque(maxlen=200)
	    loss = deque(maxlen=200)

	character_path = 'samples/char.TXT'
	load_character(character_path)

	R = 0
	char_index = 0
	field = None
	episode = 0
	targets_loc, width, height = fds_origin_loc[char_index % len(fds_origin_loc)]
	nFDs = len(targets_loc)
	if field == None:
		field = environment(width, height, targets_loc)
		# Initialize DQN agent
		n_actions = field.n_actions
		agent = DQNAgent(width, height, n_actions, epsilon = 0.2)
		modelpath = 'models/char.h5'
		import os.path
		if os.path.exists(modelpath):
		    agent.load(modelpath)
		
	n_freedom = field.n_freedom

	terminated = [False] * n_freedom
	need_reset = [True] * n_freedom

	while episode < EPISODES:
		#for char in fds_origin_loc:
		step = 0
		while step < EPISODE_LENGTH:
			step += 1
			for n in range(n_freedom):
				if terminated[n]:
					continue

				if need_reset[n]:
					state = field.reset_freedom(n)
					need_reset[n] = False
				state = field.obsv(n)
				action = agent.get_action(state)
				next_state, reward, terminated[n] = field.step_freedom(n, action)
				R += reward
				field.render()

			if False not in terminated:
				agent.update_target_model()
				need_reset = [True] * n_freedom
				terminated = [False] * n_freedom
				break
		episode += 1
		print "episode: ", episode, "/", EPISODES, " steps: ", step, "rewards", R / nFDs, "e: ", agent.epsilon	

		if enable_plot:
			episodes.append(episode)
			steps.append(step)
			rewards.append(R / nFDs)
			#loss.append(l)
			plt.plot(episodes, steps, 'r')
			plt.plot(episodes, rewards, 'b')
			#plt.plot(episodes, loss, 'black')
			plt.xlim([int(episode / 100) * 100, int(episode / 100) * 100 + 100])
			plt.xlabel("Episodes")
			plt.legend(('Steps per episode', 'Rewards per episode'))
			fig.canvas.draw()
		 # Save trained agent every once in a while
		if episode % 100 == 0:
		    if enable_plot:
		        ax.clear()

		if True not in terminated:
			time.sleep(1)
			R = 0
			char_index += 1
			targets_loc, width, height = fds_origin_loc[char_index % len(fds_origin_loc)]
			field.update_env(targets_loc)
			n_freedom = field.n_freedom

			terminated = [False] * n_freedom
			need_reset = [True] * n_freedom


if __name__ == "__main__":
	'''
	from argparse import ArgumentParser
	parser = ArgumentParser(description='character')
	parser.add_argument('char', help = 'which character')

	args = parser.parse_args()
	'''
	main()					
