import time
import sys, os
from pathlib import Path

from tkinter import *
from tkinter import ttk
from tkinter import font as tkFont

class DisplayField(Text):
	def __init__(self, *args, **kwargs):
		super().__init__(wrap=WORD, *args, **kwargs)
		
		default_font = tkFont.nametofont(self.cget("font"))
		em = default_font.measure("m")
		
		bold_font = tkFont.Font(**default_font.configure())
		bold_font.configure(weight="bold", size= 2 * em)

		self.tag_configure('fresh', font=bold_font, foreground='Grey')
		self.tag_configure('error', font=bold_font, foreground='Red')
		self.tag_configure('correct', font=bold_font, foreground='Green')
		
		self.bind('<Key>', lambda e: 'break')

	def update(self, display_string, comp_string):
		self.delete('1.0', END)

		output = []
		for i, comp_char in enumerate(comp_string):
			if i >= len(display_string):
				break

			disp_char = display_string[i]
			if comp_char == disp_char:
				output += (disp_char, 'correct')
			else:
				output += (disp_char, 'error')
		
		output += (display_string[len(comp_string):], 'fresh')

		self.insert(END, *output)


class TypingTrainer:
	def __init__(self, root, display_string):
		root.title("Smart typing trainer")
	
		root.columnconfigure(0, weight=1)
		root.rowconfigure(0, weight=1)

		mainframe = ttk.Frame(root, padding='0.3i')
		mainframe.grid(column=0, row=0, stick=(N, W, E, S))
		
		mainframe.columnconfigure(tuple(range(3)), weight=1)
	
		ttk.Label(mainframe, text="Type Better, Type Faster", anchor='center').grid(column=0, row=0, columnspan=3, stick=(W, E))

		self.disp_string = display_string
		self.comp_string = ""

		self.display_field = DisplayField(mainframe, )
		self.display_field.grid(column=0, row=1, columnspan=3, sticky='news')

		self.last_time = time.time()
		self.last_char = None

		self.pairs = {} # key: 'xx' value: (occurences, average time)

		
		sv = StringVar()
		sv.trace_add('write', lambda *_, var=sv: self.callback(var))

		# entry = Entry(mainframe, textvariable=sv, width=80)
		# entry.grid(column=0, row=4, columnspan=3)
		entry = Text(mainframe, )
		entry.grid(column=0, row=2, columnspan=3, sticky='news')
		entry.bind('<KeyRelease>', lambda *_, var=entry: self.callback(var))


		self.display_field.update(self.disp_string, self.comp_string)
		
	def callback(self, var):
		# Update the comparison string
		# TODO punish the user for incorrect input
		self.comp_string = var.get("1.0", END)[:-1] # Ignore the trailing newline
		self.display_field.update(self.disp_string, self.comp_string)

		current_time = time.time()
		delta_time = current_time - self.last_time
		self.last_time = current_time

		if self.last_char is None:
			self.last_char = self.comp_string[-1]
			return
		
		if not self.comp_string:
			return

		pair = (self.last_char + self.comp_string[-1]).lower()
		self.last_char = self.comp_string[-1]

		occurences, avg = self.pairs.get(pair, (0, 0.0))
		
		avg = (avg * occurences + delta_time) / (occurences + 1)
		occurences += 1
		
		self.pairs[pair] = (occurences, avg)
		
		if self.disp_string == self.comp_string:
			self.output_results()

	def output_results(self):
		sorted_output = {k: v for k, v in sorted(self.pairs.items(), key=lambda item: item[1][1], reverse=True)}

		for tup in sorted_output.items():
			print(tup)

import random

if __name__ == '__main__':
	texts_directory = 'res/typing/'

	Path(texts_directory).mkdir(parents=True, exist_ok=True)

	filename = random.choice(os.listdir(texts_directory))

	disp_string = None
	with open (texts_directory + '/' + filename, 'r', newline='\n') as f:
		disp_string = f.read().replace('\n', ' ')

	root = Tk()
	TypingTrainer(root, disp_string)
	root.mainloop()