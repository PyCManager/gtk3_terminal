#! /usr/bin/python

from gi.repository import Gtk as gtk, Vte as vte, Gdk as gdk, Gio as gio, GLib as glib, Keybinder
import test_theme, test_config as config, test_term_box, test_tool_box
import signal
import json
import sys
import re
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
		self.working_dir = config.terminal_default_path
		
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
			self.term_box.scroll_window_term.add(self.active_term)
			self.active_term.show_now()
			
			
		self.active_term.grab_focus()
		self.active_term.connect("child-exited", self.on_term_child_exited)
		self.active_term.connect("text-deleted", self.on_text_deleted)
		self.parent.active_term = self.active_term
		
		self.set_tab_label()
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



class TestHeaderBar(gtk.HeaderBar):

	def __init__(self, parent, app):
		gtk.Window.__init__(self)
		
		self.props.title = config.title_application
		self.set_subtitle(config.subtitle_application)
		self.set_name("header_bar")
		self.parent = parent

		self.set_show_close_button(config.show_close_button)

		self.box_end = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
		gtk.StyleContext.add_class(self.box_end.get_style_context(), "linked")
		
		self.pack_end(self.box_end)

	

class MainWindow(gtk.ApplicationWindow):
	
	def __init__(self, app):
		gtk.Window.__init__(self, title="test", type=gtk.WindowType.TOPLEVEL, application=app)
		self.set_name("main_window")

		self.connect("delete-event", gtk.main_quit)
		self.connect("window-state-event", self.on_window_state_event)
		self.connect("focus-in-event", self.on_focus_in_event)
		self.connect("focus-out-event", self.on_focus_out_event)
#		self.connect("key-press-event", self.on_key_press_event)
#		self.connect("key-release-event", self.on_key_release_event)

		self.is_present = True
		self.have_focus = True
		self.is_fullscreen = False
		

		print("Theme used:", theme.theme_used)
		self.style_provider = gtk.CssProvider()
		self.load_css(theme.css_file)

		self.load_shortcuts()
		self.bind_key()

		self.count_changed_state = 0
		
		self.main_box = TestMainBox(self)
		self.add(self.main_box)
		self.active_term = self.main_box.active_term
		self.set_opacity(config.window_opacity)

	
	def load_css(self, css_file):

		css = open((css_file), 'rb')
		css_data = css.read()
		css.close()
		
		self.style_provider.load_from_data(css_data)

		gtk.StyleContext.add_provider_for_screen(
			gdk.Screen.get_default(), self.style_provider,     
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
		
		
	def accel_fullscreen(self, accel_group, window, key, mod):
		print("Accelerator for fullscreen")
		if self.is_fullscreen:
			self.unfullscreen()
		else:
			self.fullscreen()
		

	def on_focus_in_event(self, window, event):
#		print("Window is focused")
		self.have_focus = True
	
	
	def on_focus_out_event(self, window, event):
#		print("Window is not focused anymore")
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
			self.main_box.active_term.grab_focus()
			self.is_present = True


	def on_window_state_event(self, window, event):
		FOCUSED 	= gdk.WindowState.FOCUSED
		TILED 		= gdk.WindowState.TILED
		MAXIMIZED 	= gdk.WindowState.MAXIMIZED
		ICONIFIED 	= gdk.WindowState.ICONIFIED
		WITHDRAWN	= gdk.WindowState.WITHDRAWN
		FULLSCREEN	= gdk.WindowState.FULLSCREEN
		HIDDEN 		= "HIDDEN"
		DEICONIFIED	= "DEICONIFIED"
#		print("MASK:", event.changed_mask)
#		print("STATE:", event.new_window_state)
#		print("Window size:", self.get_size())

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
		
		if event.changed_mask & FULLSCREEN:
			if event.new_window_state & FULLSCREEN:
#				print("Window is in fullscreen")
				self.is_fullscreen = True
				self.is_present = True
			elif event.new_window_state & FOCUSED:
				self.is_fullscreen = False
				self.is_present = True
				
		return True





class TestApp(gtk.Application):

	def __init__(self):
		gtk.Application.__init__(self,
								application_id="org.keiwop.nameless_term",
								flags=gio.ApplicationFlags.FLAGS_NONE)
		self.connect("activate", self.activate_app)
		
		
	def activate_app(self, app):

		self.header_bar = TestHeaderBar(self, app)
		self.main_window = MainWindow(self)
		self.restore_window_state(config.window_restore_state)
		self.main_window.set_titlebar(self.header_bar)
		self.create_main_menu()
		self.main_box = self.main_window.main_box

		self.add_window(self.main_window)
		self.main_window.show_all()
	
	
	def do_startup(self):
		gtk.Application.do_startup(self)
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		self.connect_actions()
#		self.load_shortcuts()
		
		
	def connect_actions(self):
		fullscreen_action = gio.SimpleAction.new("on_fullscreen_activated", None)
		fullscreen_action.connect("activate", self.on_fullscreen_activated)
		self.add_action(fullscreen_action)
		
		preferences_action = gio.SimpleAction.new("on_preferences_activated", None)
		preferences_action.connect("activate", self.on_preferences_activated)
		self.add_action(preferences_action)

		theme_action_default = gio.SimpleAction.new("theme_default", None)
		theme_action_default.connect("activate", self.change_current_theme, "default")
		self.add_action(theme_action_default)

		theme_action_solarized_light = gio.SimpleAction.new("theme_solarized_light", None)
		theme_action_solarized_light.connect("activate", self.change_current_theme, "solarized_light")
		self.add_action(theme_action_solarized_light)

		theme_action_solarized_dark = gio.SimpleAction.new("theme_solarized_dark", None)
		theme_action_solarized_dark.connect("activate", self.change_current_theme, "solarized_dark")
		self.add_action(theme_action_solarized_dark)
			
	
	def restore_window_state(self, restore_state):
		if restore_state:
			print("Restoring window state")
			print("Current position:", self.main_window.get_position())
			print("Current size:", self.main_window.get_size())
			data = config.window_state
			self.window_position = data[0]
			self.window_size = data[1]
			print("position:", data[0])
			print("size:", data[1])
			self.main_window.move(self.window_position[0], self.window_position[1])
			self.main_window.set_default_size(self.window_size[0], self.window_size[1])
		else:
			self.main_window.set_default_size(config.window_default_width, config.window_default_height)
		
		
	def create_main_menu(self):
		self.button_menu = gtk.MenuButton()
		image = theme.get_image("header_menu")
		self.button_menu.add(image)
		
		self.button_save_state = gtk.Button("Save")
		self.button_save_state.connect("clicked", self.on_button_save_state_clicked)
	
		self.main_menu = gio.Menu()
		self.button_menu.set_menu_model(self.main_menu)
		
		self.theme_submenu = gio.Menu()		
		self.theme_submenu.append("Default", "app.theme_default")
		self.theme_submenu.append("Solarized light", "app.theme_solarized_light")
		self.theme_submenu.append("Solarized dark", "app.theme_solarized_dark")

		self.main_menu.append("Fullscreen", "app.on_fullscreen_activated")
		self.main_menu.append_submenu("Theme", self.theme_submenu)
		self.main_menu.append("Preferences", "app.on_preferences_activated")

		
		self.header_bar.box_end.add(self.button_save_state)		
		self.header_bar.box_end.add(self.button_menu)
#		self.header_bar.pack_end(self.box_end)


	def on_button_save_state_clicked(self, widget):
		print("Saving window state")
		self.main_window.window_state = []
		self.main_window.window_state.append(self.main_window.get_position())
		self.main_window.window_state.append(self.main_window.get_size())
		new_line = str(self.main_window.window_state)
		self.replace_line(config.file_config, "window_state", new_line)
		
		
	def change_current_theme(self, action, arg, theme_name):
		global theme
		print("Setting theme:", theme_name)
		theme = test_theme.TestTheme(theme_name)
		self.main_window.load_css(theme.css_file)
		self.main_window.main_box.term_box.theme = theme
		
		self.active_term = self.main_window.main_box.active_term
		self.active_term.set_colors(theme.terminal_fg, theme.terminal_bg, theme.palette)
		self.active_term.set_color_cursor(theme.terminal_cursor)
		self.active_term.set_cursor_shape(theme.terminal_cursor_shape)

		self.main_window.show_all()
		new_line = "theme_list[%d]" % config.theme_list.index(theme_name)
		self.replace_line(config.file_config, "default_theme", new_line)


	def on_preferences_activated(self, widget, arg):
		print("Opening the preferences")
		
		
	def on_fullscreen_activated(self, widget, arg):
		print("Going in Fullscreen mode")
		if self.main_window.is_fullscreen:
			self.main_window.unfullscreen()
			self.main_window.active_term.grab_focus()
		else:
			self.main_window.fullscreen()
			self.main_window.set_focus(self.main_window.active_term)
			self.main_window.active_term.grab_focus()
		
		
	def on_test_activated(self, widget, arg):
		print("Test is a success !")
		
		
	def replace_line(self, file_name, value_name, new_value):
		with open(file_name, "r") as f:
			data = f.readlines()
		f.close()
		with open(file_name, "w") as f:
			for line in data:
				if self.is_in_line(line, value_name):
					print("FOUND:", line, end="")
					new_line = value_name + config.delimiter + new_value
					print("Replaced by:", new_line)
					print(new_line, file=f, end="\n")
				else:
					print(line, file=f, end="")
		f.close()
	
	
	def is_in_line(self, line, word):
		return re.search("^{0} =*".format(word), line)


if __name__ == '__main__':
	app = TestApp()
	app.run(sys.argv)

