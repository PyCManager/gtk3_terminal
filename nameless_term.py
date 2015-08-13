#! /usr/bin/python

from gi.repository import Gtk as gtk, Gio as gio, GLib as glib, Notify
import test_theme, test_config as config, test_main_window
import signal
import sys
import re

theme = test_theme.TestTheme(config.default_theme)


class TestApp(gtk.Application):

	def __init__(self):
		gtk.Application.__init__(self,
								application_id="org.keiwop.nameless_term",
								flags=gio.ApplicationFlags.FLAGS_NONE)

		
	def do_activate(self):

		self.create_main_window()
		self.restore_window_state(config.window_restore_state)
		self.create_app_menu()
		self.create_shortcut_box()
		theme.load_icons(self)
		
		self.connect_actions_accelerators()
		self.connect_actions_main_menu()
		self.connect_actions_header_bar()
		self.connect_actions_theme_submenu()
		self.connect_actions_shortcut_box()

		self.add_window(self.main_window)
		self.main_window.show_all()
	
	
	def do_startup(self):
		gtk.Application.do_startup(self)
		signal.signal(signal.SIGINT, signal.SIG_DFL)

		if config.restore_night_mode:
			self.night_mode_state = config.night_mode_state
			print("Night mode:", self.night_mode_state)
			gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", self.night_mode_state)


		for action_name in config.shortcut_dict:
			shortcut = config.shortcut_dict[action_name]
#			print("SHORTCUT:", shortcut)
#			print("ACTION:", action_name)
			self.set_accels_for_action(action_name, shortcut)
#			print("ACCELS for :", action_name, self.get_accels_for_action(action_name))


	def create_main_window(self):
#		self.builder_main_window = gtk.Builder()
#		self.builder_main_window.add_from_file(config.file_ui_main_window)	
#		self.main_window = self.builder_main_window.get_object("main_window")
		self.create_header_bar()
		self.main_window = test_main_window.MainWindow(self, theme)
		self.main_window.set_titlebar(self.header_bar)
	
	
	def create_header_bar(self):
		self.builder_header_bar = gtk.Builder()
		self.builder_header_bar.add_from_file(config.file_ui_header_bar)

		self.header_bar = self.builder_header_bar.get_object("header_bar")
		self.button_header_menu = self.builder_header_bar.get_object("button_header_menu")
		self.button_save_state = self.builder_header_bar.get_object("button_save_state")
		self.button_exit_app = self.builder_header_bar.get_object("button_exit_app")
		self.button_save_state.set_name("button_save_state")
		self.button_exit_app.set_name("button_exit_app")
		
		if config.rename_application:
			self.header_bar.props.title = config.title_application
			self.header_bar.set_subtitle(config.subtitle_application)
		self.header_bar.set_name("header_bar")

		self.create_popover_menu()
		self.button_header_menu.set_popover(self.popover_menu)
		self.popover_menu.set_name("popover_menu")
	
	
	def create_popover_menu(self):
		self.builder_popover_menu = gtk.Builder()
		self.builder_popover_menu.add_from_file(config.file_ui_popover_menu)

		self.builder_theme_submenu = gtk.Builder()
		self.builder_theme_submenu.add_from_file(config.file_ui_theme_submenu)

		self.popover_menu = self.builder_popover_menu.get_object("popover_menu")
				
		self.button_theme_submenu = self.builder_popover_menu.get_object("button_theme_submenu")
		self.popover_theme_submenu = self.builder_theme_submenu.get_object("popover_theme_submenu")
		self.button_theme_submenu.set_popover(self.popover_theme_submenu)
		self.popover_theme_submenu.set_name("popover_theme_submenu")
		
		
		self.button_fullscreen = self.builder_popover_menu.get_object("button_fullscreen")
		self.button_fullscreen.set_name("button_fullscreen")
		
		self.button_night_mode = self.builder_popover_menu.get_object("button_night_mode")
		self.button_night_mode.set_name("button_night_mode")

		if config.override_menu_relief:
			self.button_fullscreen.set_relief(theme.relief_button_main_menu)
			self.button_night_mode.set_relief(theme.relief_button_main_menu)
				
	
	def create_app_menu(self):
		
		self.app_menu = gio.Menu()
		
		self.theme_submenu = gio.Menu()		
		self.theme_submenu.append("Default", "app.theme_default")
		self.theme_submenu.append("Solarized light", "app.theme_solarized_light")
		self.theme_submenu.append("Solarized dark", "app.theme_solarized_dark")

		self.app_menu.append("Fullscreen", "app.fullscreen")
		self.app_menu.append_submenu("Theme", self.theme_submenu)
		self.app_menu.append("Preferences", "app.on_preferences_activated")
		
		self.set_app_menu(self.app_menu)
		
		
	def create_shortcut_box(self):
		self.builder_shortcut_box = gtk.Builder()
		self.builder_shortcut_box.add_from_file(config.file_ui_shortcut_box)
		self.event_shortcut_box = self.builder_shortcut_box.get_object("event_shortcut_box")
		self.event_shortcut_box.set_name("shortcut_box")
		self.event_shortcut_box.connect("scroll-event", self.scroll_test)
		
		self.button_new_term = self.builder_shortcut_box.get_object("button_new_term")
		self.button_close_term = self.builder_shortcut_box.get_object("button_close_term")
		
		if config.tab_box_pack_start:
			self.main_window.main_box.tool_box.pack_end(self.event_shortcut_box, False, True, 0)
		else:
			self.main_window.main_box.tool_box.pack_start(self.event_shortcut_box, False, True, 0)
		
		
	def connect_actions_header_bar(self):
		self.window_state = gio.SimpleAction.new_stateful("save_window_state",
									 		None, glib.Variant.new_boolean(False))
		self.window_state.connect("change-state", self.save_window_state)
		self.add_action(self.window_state)
		
		self.exit_app = gio.SimpleAction.new_stateful("exit_application",
									 		None, glib.Variant.new_boolean(False))
		self.exit_app.connect("change-state", self.exit_application)
		self.add_action(self.exit_app)
	
	
	def connect_actions_main_menu(self):
		self.action_fullscreen = gio.SimpleAction.new_stateful("fullscreen",
									 None, glib.Variant.new_boolean(False))
		self.action_fullscreen.connect("change-state", self.toggle_fullscreen)
		self.add_action(self.action_fullscreen)

		
		self.action_night_mode = gio.SimpleAction.new_stateful("toggle_night", 
						None, glib.Variant.new_boolean(self.night_mode_state))
		self.action_night_mode.connect("change-state", self.toggle_night_mode)
		self.add_action(self.action_night_mode)
	
	
	def connect_actions_theme_submenu(self):
		self.actions_theme = []
		for theme_name in config.theme_list:
			if theme_name == theme.theme_used:
				action_state = True
			else:
				action_state = False
			action_name = "theme_" + theme_name
#			print("Theme:", theme_name)
			action_theme = gio.SimpleAction.new_stateful(action_name, 
						None, glib.Variant.new_boolean(action_state))
			action_theme.connect("change-state", self.change_current_theme, theme_name)
			self.add_action(action_theme)
			self.actions_theme.append(action_theme)
	
	
	def connect_actions_shortcut_box(self):
		self.action_new_term = gio.SimpleAction.new_stateful("new_term",
									 None, glib.Variant.new_boolean(False))
		self.action_new_term.connect("change-state", self.new_term)
		self.add_action(self.action_new_term)
		
		self.action_close_term = gio.SimpleAction.new_stateful("close_term",
									 None, glib.Variant.new_boolean(False))
		self.action_close_term.connect("change-state", self.close_term)
		self.add_action(self.action_close_term)
		
	
	def connect_actions_accelerators(self):
		self.action_next_term = gio.SimpleAction.new_stateful("next_term",
									 None, glib.Variant.new_boolean(False))
		self.action_next_term.connect("change-state", self.next_term)
		self.add_action(self.action_next_term)
		
		self.action_prev_term = gio.SimpleAction.new_stateful("prev_term",
									 None, glib.Variant.new_boolean(False))
		self.action_prev_term.connect("change-state", self.prev_term)
		self.add_action(self.action_prev_term)
		
		self.action_copy_clipboard = gio.SimpleAction.new_stateful("copy_clipboard",
									 None, glib.Variant.new_boolean(False))
		self.action_copy_clipboard.connect("change-state", self.copy_clipboard)
		self.add_action(self.action_copy_clipboard)
		
		self.action_paste_clipboard = gio.SimpleAction.new_stateful("paste_clipboard",
									 None, glib.Variant.new_boolean(False))
		self.action_paste_clipboard.connect("change-state", self.paste_clipboard)
		self.add_action(self.action_paste_clipboard)
	

	
	def scroll_test(self, action, state):
		print("Scrolling")
		
	def copy_clipboard(self, action, state):
		print("Copying to clipboard")
		self.active_term = self.main_window.main_box.active_term
		self.active_term.copy_clipboard()
	
	def paste_clipboard(self, action, state):
		print("Pasting the clipboard")
		self.active_term = self.main_window.main_box.active_term
		self.active_term.paste_clipboard()
	
	def new_term(self, action, state):
		print("Opening new terminal")
		self.main_window.main_box.add_new_term(config.terminal_default_name)

	def close_term(self, action, state):
		print("Closing active terminal")
		self.nb_active_term = self.main_window.main_box.nb_active_term
		self.main_window.main_box.remove_term(self.nb_active_term, False)
	
	def next_term(self, action, state):
		print("Going to next term")
		self.main_window.main_box.move_next_term()
		
	def prev_term(self, action, state):
		print("Going to prev term")	
		self.main_window.main_box.move_prev_term()
		
		
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
	
	
	def exit_application(self, action, state):
		self.quit()
	
	
	def save_window_state(self, action, state):
		print("Saving window state")
		self.main_window.window_state = []
		self.main_window.window_state.append(self.main_window.get_position())
		self.main_window.window_state.append(self.main_window.get_size())
		new_line = str(self.main_window.window_state)
		self.replace_line(config.file_config, "window_state", new_line)


	def change_current_theme(self, action, state, theme_name):
		global theme
		print("Setting theme:", theme_name)
		
		for action_theme in self.actions_theme:
#			print("THEME:", action_theme)
			if action_theme == action:
				state = glib.Variant.new_boolean(True)
			else:
				state = glib.Variant.new_boolean(False)
			action_theme.set_state(state)

		theme = test_theme.TestTheme(theme_name)
		self.main_window.load_css(theme.css_file)
		self.main_window.theme = theme
		self.main_window.main_box.theme = theme
		self.main_window.main_box.term_box.theme = theme
		self.main_window.main_box.tool_box.theme = theme
	
		self.active_term = self.main_window.main_box.active_term
		self.active_term.set_colors(theme.terminal_fg, theme.terminal_bg, theme.palette)
		self.active_term.set_color_cursor(theme.terminal_cursor)
		self.active_term.set_cursor_shape(theme.terminal_cursor_shape)
		
		theme.load_icons(self)
		self.main_window.show_all()
		new_line = "theme_list[%d]" % config.theme_list.index(theme_name)
		self.replace_line(config.file_config, "default_theme", new_line)


	def toggle_fullscreen(self, action, state):
		print("toggling fullscreen mode")
		state = glib.Variant.new_boolean(self.main_window.is_fullscreen)
		self.action_fullscreen.set_state(state)
		
		if self.main_window.is_fullscreen:
			self.main_window.unfullscreen()
			self.header_bar.show()
			self.main_window.active_term.grab_focus()
		else:
			Notify.init(config.title_application)
			notification_fullscreen = Notify.Notification.new(config.title_application, 
											"App is in fullscreen, press F11 to quit", 
											"view-fullscreen-symbolic")
			notification_fullscreen.add_action("app.toggle_fullscreen",
												"toggle_fullscreen",
												app.toggle_fullscreen,
												None,
												None)
			notification_fullscreen.show()
			
			self.main_window.fullscreen()
			self.header_bar.hide()
			self.main_window.set_focus(self.main_window.active_term)
			self.main_window.active_term.grab_focus()


	def toggle_night_mode(self, action, state):
		print("Toggling night mode")
		self.night_mode_state = not self.night_mode_state
		state = glib.Variant.new_boolean(self.night_mode_state)
		self.action_night_mode.set_state(state)
			
		gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", state)
		new_line = str(self.night_mode_state)
		self.replace_line(config.file_config, "night_mode_state", new_line)


	def on_preferences_activated(self, widget, arg):
		print("Opening the preferences")
		
		
	def on_test_activated(self, widget, arg):
		print("Test is a success !")
		
	def on_button_test_clicked(self, widget, arg):
		print("Test is a success !")
		
		
	def replace_line(self, file_name, value_name, new_value):
		with open(file_name, "r") as f:
			data = f.readlines()
		f.close()
		with open(file_name, "w") as f:
			for line in data:
				if self.is_in_line(line, value_name):
					print("Found config:", line, end="")
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


