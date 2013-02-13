from pattern.web import plaintext
from pattern.en import parse
import time
import string
from settings import *

class Time():
	def __init__(self, t):
		self.string = t  
		# Time string should be in the form "2009-07-09T08:39:20+0000"
		t = time.strptime(self.string, "%Y-%m-%dT%H:%M:%S+0000")
		self.year = t[0]
		self.month = t[1]
		self.day = t[2]
		self.hour = t[3]
		self.minute = t[4]
		self.second = t[5]
		# seconds since the January 1st, 1970 Epoch
		self.in_secs = time.mktime(t)
		
	def __str__(self):
		return '[' + str(self.year) + '-' + str(self.month) + '-' + str(self.day) + 'T' + str(self.hour) + ':' + str(self.minute) + ':' + str(self.second) + ']'
		
class Message():
	def __init__(self, sender, time, content, reciever = None):
		self.sender = sender
		self.reciever = reciever
		self.time = Time(time)
		self.content = content
		self.words = []
		s = parse(self.content
				, tokenize = True
				, tags = False
				, chunks = False
				, relations = False
				, lemmata = False
				, light = True)
		# TODO This will cause problems with words like "it's"! 
		s = s.encode("utf-8").translate(string.maketrans("",""), string.punctuation)
		for w in s.lower().split():
			self.words.append(w)
			
	def word_count(self):
		return len(self.words)
		
	def __iter__(self):
		for w in self.words:
			yield w 

class Messages(list):
	def __init__(self):
		# This object inherits from list type, so actual messages are 
		# simply appended to the internal list. 
		pass
	
	def words(self, **kwargs):
		# An attribute can be specified which must be a particular value
		# for the words of a message to be yielded. 
		attr = kwargs.get("attr", False)
		# If attribute has been specified, a value must also be specified. 
		if attr != False:
			try:
				value = kwargs["value"]
			except:
				raise Exception("If attr is specified, a value must also be specified")
		# Iterate over messages. If attr has been specifed, and attr of 
		# current message is equal to value, than inner for loop will 
		# yield words of current message. Otherwise, outer for loop 
		# will continue to next item. 		
		for m in self:
			if attr != False: 
				if m.__dict__[attr] != value:
					continue
			for w in m:
				yield w
	
	def print_messages(self):
		for i in self:
			s = i.content
			print i.sender, i.time, str(i.time.in_secs) + ":", s

class Conversation():
	def __init__(self, msgs):
		self.messages = Messages()
		for i in msgs:
			self.messages.append(i)
			
		self.initiator = self.messages[0].sender
		
	def append_msg(self,message):
		self.messages.append(message) 
	
class Conversations(list):
	def __init__(self):
		pass 
	
	def construct_conversations(self, msgs):
		cur_conv = []
		for i in range(0, len(msgs)-1):
			cur_m = msgs[i]
			next_m = msgs[i+1]
			cur_conv.append(cur_m)
			time_diff = (next_m.time.in_secs - cur_m.time.in_secs)
			if time_diff >= SECS_BETWEEN_CONV or time_diff < 0:
				self.append(cur_conv)
				cur_conv = []
		
		if len(cur_conv) > 0: 		
			self.append(cur_conv)
		
		# Then these lists are turned into Conversation objects
		for i in range(0, len(self)):
			self[i] = Conversation(self[i])
	
class Thread():
	def __init__(self):
		self.p1 = ''
		self.p2 = '' 
		self.conversations = Conversations()
		self.messages = Messages()
		
	def add_message(self, sender, time, content, reciever = None):
		self.messages.append(Message(sender, time, content, reciever))
		
	def combine(self, thread):
		assert self.p1 == thread.p1
		assert self.p2 == thread.p2
		for m in thread.messages:
			self.messages.append(m)
		for c in thread.conversations:
			self.conversations.append(c) 
			
	def construct_conversations(self):
		self.conversations.construct_conversations(self.messages) 
	
	def __str__(self):
		return self.p1.encode("utf-8") + "-" + self.p2.encode("utf-8")
	
class Threads(list):
	def __init__(self):
		pass