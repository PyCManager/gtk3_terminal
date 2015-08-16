#! /usr/bin/env python3

from gi.repository import Gtk as gtk, Gio as gio, GLib as glib, Notify
#from gi.repository import AppIndicator3 
import nameless_theme, nameless_config as config, nameless_main_window
import logging
import signal
import sys
import re

theme = nameless_theme.TestTheme(config.default_theme)
logging.basicConfig(stream=sys.stderr, level=config.logging_level)


class TestApp(gtk.Application):

	def __init__(self):
		gtk.Application.__init__(self,
								application_id="org.keiwop.nameless_term",
								flags=gio.ApplicationFlags.FLAGS_NONE)


	def do_startup(self):
		gtk.Application.do_startup(self)
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		
		logging.info("Hello, this is the Nameless Terminal")
		
		if config.restore_night_mode:
			self.night_mode_state = config.night_mode_state
			logging.info("Night mode: %s"% self.night_mode_state)
			gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", self.night_mode_state)

		for action_name in config.shortcut_dict:
			shortcut = config.shortcut_dict[action_name]
			self.set_accels_for_action(action_name, shortcut)

		self.is_drop_down = config.is_drop_down
#		self.drop_down_state = config.drop_down_state
		self.count_resize_event = 0
#		self.drop_down_position = config.drop_down_default_position
#		self.drop_down_size = config.drop_down_state[1]
	
		
	def do_activate(self):

		self.create_main_window()
		self.main_window.set_icon_from_file(config.file_program_icon)
		self.create_app_menu()
#		self.create_app_indicator()
		self.restore_window_state(config.window_restore_state)	
		
		self.create_shortcut_box()
		theme.load_icons(self)
		
		self.connect_actions_accelerators()
		self.connect_actions_main_menu()
		self.connect_actions_header_bar()
		self.connect_actions_theme_submenu()
		self.connect_actions_shortcut_box()

		self.add_window(self.main_window)
		self.main_window.show()
		
#		I've got garbage in the first terminal, so I close it. 
#		I know it's ugly, but I might spend some time on it later
		self.close_term(None, None)
#		self.main_window.main_box.active_term.feed_child(command, len(command))
		self.main_window.connect("check-resize", self.on_resize_event)


	
#	def create_app_indicator(self):
#		self.indicator = AppIndicator3.Indicator.new(
#			"TestNAME",
#			"test",
#			AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
#		self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
#		self.indicator.set_icon_theme_path(config.path_to_icons)
#		self.indicator.set_icon(config.file_program_icon)
#		self.menu_indicator = gtk.Menu()
#		
#		self.item_fullscreen = gtk.MenuItem("Fullscreen")
#		self.item_fullscreen.connect("activate", self.toggle_fullscreen, None)
#		self.item_preferences = gtk.MenuItem("Preferences")
#		
#		self.menu_indicator.append(self.item_fullscreen)
#		self.menu_indicator.append(self.item_preferences)
#		self.menu_indicator.show_all()
#		
#		self.indicator.set_menu(self.menu_indicator)
	
	

	def create_main_window(self):
		self.create_header_bar()
		self.main_window = nameless_main_window.MainWindow(self, theme)
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
		self.button_drop_down = self.builder_shortcut_box.get_object("button_drop_down")
		
		if config.tab_box_pack_start:
			self.main_window.main_box.tool_box.pack_end(self.event_shortcut_box, False, True, 0)
		else:
			self.main_window.main_box.tool_box.pack_start(self.event_shortcut_box, False, True, 0)
		
		
	def connect_actions_header_bar(self):
		self.action_window_state = gio.SimpleAction.new_stateful("save_window_state",
									 		None, glib.Variant.new_boolean(False))
		self.action_window_state.connect("change-state", self.save_window_state)
		self.add_action(self.action_window_state)
		
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
#			logging.info("Theme: %s"% theme_name)
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
		
		self.action_drop_down = gio.SimpleAction.new_stateful("drop_down",
									 None, glib.Variant.new_boolean(False))
		self.action_drop_down.connect("change-state", self.drop_down)
		self.add_action(self.action_drop_down)
		
	
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
		logging.debug("Scrolling")
		
	def copy_clipboard(self, action, state):
		logging.debug("Copying to clipboard")
		self.active_term = self.main_window.main_box.active_term
		self.active_term.copy_clipboard()
	
	def paste_clipboard(self, action, state):
		logging.debug("Pasting the clipboard")
		self.active_term = self.main_window.main_box.active_term
		self.active_term.paste_clipboard()
	
	def new_term(self, action, state):
		logging.info("Opening new terminal")
		self.main_window.main_box.add_new_term(config.terminal_default_name)

	def close_term(self, action, state):
		logging.info("Closing active terminal")
		self.nb_active_term = self.main_window.main_box.nb_active_term
		self.main_window.main_box.remove_term(self.nb_active_term, False)
	
	def next_term(self, action, state):
		logging.info("Going to next term")
		self.main_window.main_box.move_next_term()
		
	def prev_term(self, action, state):
		logging.info("Going to prev term")	
		self.main_window.main_box.move_prev_term()
		
		
	def drop_down(self, action, state):
		logging.info("Toggling drop-down mode")

		self.is_drop_down = not self.is_drop_down
		logging.debug("drop_down_state: %s"% self.is_drop_down)

		state = glib.Variant.new_boolean(self.is_drop_down)
		self.action_drop_down.set_state(state)
		
		new_line = str(self.is_drop_down)
		self.replace_line(config.file_config, "is_drop_down", new_line)
		
#		self.screen = self.main_window.get_screen()
#		self.screen_width = self.screen.get_width()
#		self.screen_height = self.screen.get_height()
		
		if self.is_drop_down:
			logging.debug("Going into drop-down mode")
			self.main_window.resize(config.drop_down_default_size[0], config.drop_down_default_size[1])
			self.main_window.move(config.drop_down_default_position[0], config.drop_down_default_position[1])
			self.main_window.show()
			self.header_bar.hide()
		else:
			logging.debug("Quitting drop-down mode")
			self.header_bar.show()
			self.restore_window_state(True)
			
	
	def on_resize_event(self, window):
		if self.is_drop_down:
			logging.debug("Resize window event")
			self.count_resize_event += 1
#			logging.debug("Window position: %s"% self.main_window.get_position())
#			logging.debug("Window size: %s"% self.main_window.get_size())
			if self.count_resize_event >= config.count_resize_event_max:
				logging.debug("Resize event is chosen")
				self.save_drop_down_height(self.main_window.get_size()[1])
				self.count_resize_event = 0
	
	
	def save_drop_down_height(self, height):
		self.drop_down_size = config.drop_down_default_size
		self.drop_down_size[1] = height
		new_line = str(self.drop_down_size)
		self.replace_line(config.file_config, "drop_down_default_size", new_line)
	
		
	def restore_window_state(self, restore_state):
		if restore_state:
#			logging.debug("Restoring window state")
#			logging.debug("Current position: %s"% self.main_window.get_position())
#			logging.debug("Current size: %s"% self.main_window.get_size())
			
			if self.is_drop_down:
				logging.info("Restoring to drop-down mode")

				self.header_bar.hide()
				data = []
				data.append(config.drop_down_default_position)
				data.append(config.drop_down_default_size)
			else:
				logging.info("Restoring normal mode")
				logging.debug("Window size: %s"% config.window_state)
				data = config.window_state	

			self.window_position = data[0]
			self.window_size = data[1]
			
			self.main_window.resize(self.window_size[0], self.window_size[1])
			self.main_window.move(self.window_position[0], self.window_position[1])
			self.main_window.show()
			
#			logging.debug("\nRestoration is done")
#			logging.debug("position: %s"% self.main_window.get_position())
#			logging.debug("size: %s"% self.main_window.get_size())
		else:
			self.main_window.resize(config.window_default_width, config.window_default_height)
	
	
	def save_window_state(self, action, state):
		self.window_state = []
		logging.info("Saving window state")
		self.window_state.append(self.main_window.get_position())
		self.window_state.append(self.main_window.get_size())
		new_line = str(self.window_state)
		self.replace_line(config.file_config, "window_state", new_line)
	

	def exit_application(self, action, state):
		self.quit()


	def change_current_theme(self, action, state, theme_name):
		global theme
		logging.info("Setting theme: %s"% theme_name)
		
		for action_theme in self.actions_theme:
#			logging.debug("THEME: %s"% action_theme)
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
		logging.info("toggling fullscreen mode")
		if state is not None:
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
		logging.info("Toggling night mode")
		self.night_mode_state = not self.night_mode_state
		state = glib.Variant.new_boolean(self.night_mode_state)
		self.action_night_mode.set_state(state)
			
		gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", state)
		new_line = str(self.night_mode_state)
		self.replace_line(config.file_config, "night_mode_state", new_line)


	def on_preferences_activated(self, widget, arg):
		logging.info("Opening the preferences")
		
		
	def on_test_activated(self, widget, arg):
		logging.debug("Test is a success !")
		
	def on_button_test_clicked(self, widget, arg):
		logging.debug("Test is a success !")
		
		
	def replace_line(self, file_name, value_name, new_value):
		with open(file_name, "r") as f:
			data = f.readlines()
		f.close()
		with open(file_name, "w") as f:
			for line in data:
				if self.is_in_line(line, value_name):
					new_line = value_name + config.delimiter + new_value
					if not self.is_drop_down:
						logging.debug("Found config: %s"% line)
						logging.debug("Replaced by: %s"% new_line)
					print(new_line, file=f, end="\n")
				else:
					print(line, file=f, end="")
		f.close()
	
	
	def is_in_line(self, line, word):
		return re.search("^{0} =*".format(word), line)


if __name__ == '__main__':
	app = TestApp()
	app.run(sys.argv)


