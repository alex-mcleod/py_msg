import msg_classes
import utilities.io
from settings import *
from pattern.web import DOM, plaintext

class MessageDump(object, utilities.io.Pickle):
	def __init__(self, dump, p1, p2 = None, **kwargs):
		self.p1 = p1
		# If self.p2 is specified, then there must only be one thread in this msg_dmp.
		# Otherwise, all threads will be retrieved and placed in self.threads. 
		self.p2 = p2
		self.dump = dump
		self.threads = msg_classes.Threads()  
		self.pickle_file_format = MSGDUMP_PICKLE_FILE_FORMAT % self.p1
		if kwargs.get("unpickle", False):
			self.unpickle()
		else:
			self.construct_dump()
			self.construct_threads()
		if kwargs.get("pickle", False):
			# The dump attribute is deleted before pickling. This attribute simply holds the DOM
			# object which is converted into threads. Including this attribute causes the program
			# to crash due to the size of the DOM object. 
			self.pickle("dump") 
	
	# p2 is optional argument. If there is only 1 thread in this dump (i.e. self.p2 has been
	# specified) then we just need to return that thread. 
	def get_thread(self, p2 = None):
		if self.p2 != None:
			return self.threads[0]
		for t in self.threads:
			if t.p2 == p2:
				return t 
		return None
	
class fbMessageDump(MessageDump):
	def __init__(self, dump, p1, p2 = None, **kwargs):
		super(fbMessageDump, self).__init__(dump, p1, **kwargs)
		
	def construct_dump(self):
		f = open(self.dump, "r")
		self.dump = DOM(f.read())
		f.close()
		
	def construct_threads(self):
		for i in self.dump.by_tag("div.thread"):
			cur_thread = msg_classes.Thread()
			cur_thread.p1 = self.p1
			thread_exists = False
			if plaintext(i.by_tag("span.profile fn")[0].content) == self.p1: 
				cur_thread.p2 = plaintext(i.by_tag("span.profile fn")[1].content)
			else:
				cur_thread.p2 = plaintext(i.by_tag("span.profile fn")[0].content)
			# TODO if p1 and p2 have the same name, error!
			# assert cur_thread.p1 != cur_thread.p2 
			for e in i.by_tag("div.message"):
				cur_thread.add_message(
						plaintext(e.by_tag("div.from")[0].content).encode("utf-8"), 
						e.by_tag("abbr.time published")[0].attributes['title'].encode("utf-8"),
						plaintext(e.by_tag("div.msgbody")[0].content).encode("utf-8")
						)
			cur_thread.construct_conversations() 
			for t in self.threads:
				if t.p2 == cur_thread.p2:
					thread_exists = True 
					t.combine(cur_thread)

			if not thread_exists:
				self.threads.append(cur_thread) 

class FbInboxDump(MessageDump):
	def __init__(self, dump, p1, p2 = None,**kwargs):
		super(FbInboxDump, self).__init__(dump, p1, p2, **kwargs)
		
	def construct_dump(self):
		# No action to perform, self.dump should already be JSON. 
		return
		
	def construct_threads(self):
		cur_thread = msg_classes.Thread()
		cur_thread.p1 = self.p1
		cur_thread.p2 = self.p2
		for m in self.dump:
			cur_thread.add_message(m['from']['id'], m['created_time'], m['message'])
		cur_thread.construct_conversations()
		self.threads.append(cur_thread) 