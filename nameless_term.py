#! /usr/bin/python

from gi.repository import Gtk as gtk, Vte as vte, Gdk as gdk, Keybinder
import test_theme, test_config as config, test_term_box, test_tool_box
import signal
import sys
import os

theme = test_theme.TestTheme(config.default_theme)



class TestMainBox(gtk.Box):
	
	def __init__(self, parent):
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
		
		self.create_term_box()
		self.create_tool_box()

		self.add_new_term("Term")
	
		
	def create_term_box(self):
		self.term_box = test_term_box.TestTermBox(self, theme)
		self.pack_start(self.term_box, True, True, 0)
	
	
	def create_tool_box(self):
		self.tool_box = test_tool_box.TestToolBox(self, theme)
		self.pack_end(self.tool_box, False, True, 0)
	
	
	def add_new_term(self, tab_label):
		self.terminal_list = self.term_box.create_term(self.terminal_list, self.path_open_terminal)
		self.tab_list = self.tool_box.tab_box.add_tab(tab_label, self.tab_list)

		self.nb_terminals = len(self.terminal_list)
		print("nb_terminals:", self.nb_terminals)

		nb_term_to_activate = self.nb_terminals - 1
		self.set_term_active(nb_term_to_activate)
		self.show_all()
			
			
	def set_term_active(self, nb_term_to_activate):
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
			self.term_box.scroll_window_term.add(self.active_term)
			
		self.active_term.grab_focus()
		self.active_term.connect("child-exited", self.on_term_child_exited)
		
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
			nb_term_to_activate = self.nb_active_term
		else:
			if tab_clicked:
				if self.nb_active_term < nb_term_rm:
					nb_term_to_activate = self.nb_active_term
				elif self.nb_active_term >= nb_term_rm:
					nb_term_to_activate = self.nb_active_term - 1
				print("NB_ACTIVE:", self.nb_active_term)
				print("NB_TO_ACTIVE:", nb_term_to_activate)
			else:
				if nb_term_rm == 0:
					nb_term_to_activate = 0
				else:
					nb_term_to_activate = nb_term_rm - 1
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



class TestHeaderBar(gtk.HeaderBar):

	def __init__(self, parent):
		gtk.Window.__init__(self)
		self.set_show_close_button(config.show_close_button)
		self.props.title = config.name_application
		self.set_name("header_bar")
		self.parent = parent

		self.box_end = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
		gtk.StyleContext.add_class(self.box_end.get_style_context(), "linked")
		
		self.button_menu = gtk.Button()
		image = theme.get_image("header_menu")
		self.button_menu.add(image)
		self.button_menu.connect("clicked", self.on_button_menu_clicked)
		
		self.box_end.add(self.button_menu)
		self.pack_end(self.box_end)

		self.show_all()

			
	def on_button_menu_clicked(self, widget): 
		print("Menu clicked")
		self.parent.main_box.remove_term(self.parent.main_box.nb_active_term, False)
		self.parent.show_all()

	

class MainWindow(gtk.Window):
	
	def __init__(self):
		gtk.Window.__init__(self, title="test", type=gtk.WindowType.TOPLEVEL)
		self.set_name("main_window")
		self.set_default_size(config.window_default_width, config.window_default_height)
		self.connect("delete-event", gtk.main_quit)
		self.connect("window-state-event", self.on_window_state_event)
		self.connect("focus-in-event", self.on_focus_in_event)
		self.connect("focus-out-event", self.on_focus_out_event)
#		self.connect("key-press-event", self.on_key_press_event)
#		self.connect("key-release-event", self.on_key_release_event)
#		self.set_type_hint(gdk.WindowTypeHint.NORMAL)
		self.is_present = True
		self.have_focus = True

		print("Theme used:", theme.theme_used)

		self.header_bar = TestHeaderBar(self)
		self.set_titlebar(self.header_bar)

		self.load_css(theme.css_file)

		self.load_shortcuts()
		self.bind_key()

		self.count_changed_state = 0
		
		self.main_box = TestMainBox(self)
		self.add(self.main_box)
		self.set_opacity(config.window_opacity)
		self.show_all()
		
	
	def load_css(self, css_file):
		style_provider = gtk.CssProvider()

		css = open((css_file), 'rb')
		css_data = css.read()
		css.close()

		style_provider.load_from_data(css_data)
	
		gtk.StyleContext.add_provider_for_screen(
			gdk.Screen.get_default(), style_provider,     
			gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)
	
	
	def load_shortcuts(self):
		self.accel_group = gtk.AccelGroup()
		
		for shortcut in config.shortcut_dict:
			function_str = config.shortcut_dict[shortcut]
			function_to_call = getattr(self, function_str)
			key, mod = gtk.accelerator_parse(shortcut)
			self.accel_group.connect(key, mod, 0, function_to_call)
			
		self.add_accel_group(self.accel_group)
	
	
	def accel_new_term(self, accel_group, window, key, mod):
		print("Accelerator for new term")
		self.main_box.add_new_term(self.main_box.nb_terminals)
		
	
	def accel_prev_term(self, accel_group, window, key, mod):
		print("Accelerator for prev term")
		self.main_box.move_prev_term()
		

	def accel_next_term(self, accel_group, window, key, mod):
		print("Accelerator for next term")
		self.main_box.move_next_term()
		

	def on_focus_in_event(self, window, event):
		print("Window is focused")
		self.have_focus = True
	
	def on_focus_out_event(self, window, event):
		print("Window is not focused anymore")
		self.have_focus = False
		
	
	def bind_key(self):
		key_bind_hide = "Menu"
		Keybinder.init()
		Keybinder.bind(key_bind_hide, self.hide_app, "key_bind_hide: %s"% key_bind_hide)
	
	
	def hide_app(self, key_bind_hide, user_data):
		self.last_event_time = Keybinder.get_current_event_time()
		print ("Event time:", self.last_event_time)

		if self.is_present:
			print("Hiding app")
			self.iconify()
			self.is_present = False

		else:
			print("Showing app")
			self.present_with_time(self.last_event_time)
			self.active_term.grab_focus()
			self.is_present = True


	def on_window_state_event(self, window, event):
		FOCUSED 	= gdk.WindowState.FOCUSED
		TILED 		= gdk.WindowState.TILED
		MAXIMIZED 	= gdk.WindowState.MAXIMIZED
		ICONIFIED 	= gdk.WindowState.ICONIFIED
		WITHDRAWN	= gdk.WindowState.WITHDRAWN
		HIDDEN 		= "HIDDEN"
		DEICONIFIED	= "DEICONIFIED"

		self.count_changed_state += 1

		if self.is_active():
			self.is_present = True
		
		if event.changed_mask & ICONIFIED:
			if event.new_window_state & ICONIFIED:
				self.is_present = False
			elif event.new_window_state == 0:
				self.is_present = True
				
		elif event.changed_mask & (FOCUSED | TILED):
			if event.new_window_state == 0:
				self.is_present = False
			elif event.new_window_state & FOCUSED:
				self.is_present = True
			elif event.new_window_state & TILED:
				self.is_present = False
				
		if event.changed_mask & WITHDRAWN:
			if event.new_window_state & WITHDRAWN:
				self.is_present = False

		return True
		
				

if __name__ == "__main__":

	signal.signal(signal.SIGINT, signal.SIG_DFL)
	MainWindow()
	gtk.main()
	
	
