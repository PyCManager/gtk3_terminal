from gi.repository import Gtk as gtk
import test_config as config, test_term_box, test_tool_box
import os



class TestMainBox(gtk.Box):
	
	def __init__(self, parent, theme):
		gtk.Box.__init__(self, orientation=gtk.Orientation.VERTICAL)
		gtk.StyleContext.add_class(self.get_style_context(), "linked")
		self.set_name("main_box")
		self.parent = parent
		
		self.terminal_list 	= []
		self.tab_list 		= []
		self.active_term 	= None
		self.nb_terminals	= 0
		self.nb_active_term	= -1
		self.path_open_terminal = config.terminal_default_path
		self.working_dir = config.terminal_default_path
		
		self.theme = theme
	
		self.create_term_box()
		self.create_tool_box()

		self.add_new_term("Term")
	
		
	def create_term_box(self):
		self.term_box = test_term_box.TestTermBox(self, self.theme)
		self.pack_start(self.term_box, True, True, 0)
	
	
	def create_tool_box(self):
		self.tool_box = test_tool_box.TestToolBox(self, self.theme)	
		self.pack_end(self.tool_box, False, True, 0)
	
	
	def add_new_term(self, tab_label):
		
		self.tab_list = self.tool_box.tab_box.add_tab(tab_label, self.tab_list)
		if self.nb_terminals >= 1:
			self.set_tab_label()
		if config.terminal_open_tab_working_dir:
			self.path_open_terminal = self.working_dir
		self.terminal_list = self.term_box.create_term(self.terminal_list, self.path_open_terminal)

		self.nb_terminals = len(self.terminal_list)
		print("nb_terminals:", self.nb_terminals)

		nb_term_to_activate = self.nb_terminals - 1
		self.set_term_active(nb_term_to_activate)
		self.show_all()
			
			
	def set_term_active(self, nb_term_to_activate):
		print("nb_active_term:", self.nb_active_term)
		print("nb_term_to_activate:", nb_term_to_activate)
		if self.nb_active_term != nb_term_to_activate:
			for tab in self.tab_list:
				tab.set_name("tab_button")
			
			self.nb_active_term = nb_term_to_activate
			self.tab_list[self.nb_active_term].set_name("active_button")
			self.active_term = self.terminal_list[self.nb_active_term]
			
			print("Removing old terminal from window")
			self.term_box.destroy()
			self.create_term_box()
				
			print("New active terminal:", self.nb_active_term)			

			self.term_box.add(self.active_term)
			self.active_term.show_now()
			
			self.scroll_bar_term_vadj = self.active_term.get_vadjustment()
			self.scroll_bar_term = gtk.Scrollbar(orientation=gtk.Orientation.VERTICAL, adjustment=self.scroll_bar_term_vadj)
			self.scroll_bar_term.set_name("scroll_bar_term")
			
			self.scroll_box_term = gtk.Box()
			self.scroll_box_term.add(self.scroll_bar_term)
			self.scroll_box_term.set_name("scroll_box_term")
			
			self.term_box.scroll_box_term.destroy()
			self.term_box.pack_end(self.scroll_box_term, False, False, 0)
			
			
		self.active_term.grab_focus()
		self.active_term.connect("child-exited", self.on_term_child_exited)
		self.active_term.connect("text-deleted", self.on_text_deleted)
		self.parent.active_term = self.active_term
		
		self.set_tab_label()
#		print("Working dir:", self.working_dir)
		if config.path_in_subtitle:
			self.parent.parent.header_bar.set_subtitle(self.working_dir)
		
		self.active_term.set_colors(self.theme.terminal_fg, self.theme.terminal_bg, self.theme.palette)
		self.active_term.set_color_cursor(self.theme.terminal_cursor)
		self.active_term.set_cursor_shape(self.theme.terminal_cursor_shape)
		
		self.show_all()

	
	def set_tab_label(self):
#		Doesn't work, apparently a bug in vte
#		self.working_dir = self.active_term.get_current_directory_uri()
		self.active_term_pid = self.active_term.pid[1]
		self.working_dir = os.readlink('/proc/%s/cwd' % self.active_term_pid)
		tab_label = self.nb_active_term
		if self.working_dir != config.terminal_default_path:
			if config.terminal_print_working_dir_path:
				tab_label = self.working_dir
			elif config.terminal_print_working_dir:
				tab_label = os.path.basename(self.working_dir)

		self.tab_list[self.nb_active_term].set_label(str(tab_label))
	

	def on_text_deleted(self, term):
		self.set_tab_label()
		if config.path_in_subtitle:
			self.parent.parent.header_bar.set_subtitle(self.working_dir)
			self.show_all()
	

	def on_term_child_exited(self, term, arg):
		print("Action: Removing terminal:", self.nb_active_term)
		self.remove_term(self.nb_active_term, False)
			
			
	def remove_term(self, nb_term_rm, tab_clicked):
		print("nb_term to be removed:", nb_term_rm)
		print("nb of terminals before:", self.nb_terminals)
		
		term_rm = self.terminal_list.pop(nb_term_rm)
		term_rm.destroy()
		tab_rm = self.tab_list.pop(nb_term_rm)
		tab_rm.destroy()
		
		self.nb_terminals = len(self.terminal_list)
		nb_term_to_activate = 0

		if self.nb_terminals < 1:
			print("Removing the only terminal")
			self.nb_active_term = -1
			self.add_new_term("test")
			nb_term_to_activate = 0
			
		elif tab_clicked:
			if self.nb_active_term < nb_term_rm:
				nb_term_to_activate = self.nb_active_term
			elif self.nb_active_term >= nb_term_rm:
				nb_term_to_activate = self.nb_active_term - 1
			
		elif config.terminal_deleted_activate_prev:
			if nb_term_rm == 0:
				nb_term_to_activate = 0
			else:
				nb_term_to_activate = nb_term_rm - 1
			self.nb_active_term = -1
			
		elif not config.terminal_deleted_activate_prev:
			if nb_term_rm == self.nb_terminals:
				nb_term_to_activate = nb_term_rm - 1
			else:
				nb_term_to_activate = nb_term_rm				 
			self.nb_active_term = -1
			
		
		self.set_term_active(nb_term_to_activate)
		print("nb of terminals after:", self.nb_terminals)
		self.show_all()			
	
	
	def move_prev_term(self):
		if self.nb_active_term:
			self.set_term_active(self.nb_active_term - 1)
		else:
			self.set_term_active(self.nb_terminals - 1)
	
	
	def move_next_term(self):
		if self.nb_active_term < self.nb_terminals - 1:
			self.set_term_active(self.nb_active_term + 1)
		else:
			self.set_term_active(0)
