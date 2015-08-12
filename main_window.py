from gi.repository import Gtk as gtk, Vte as vte, Gdk as gdk, Gio as gio, GLib as glib, Keybinder, Notify
import test_theme, test_config as config, test_term_box, test_tool_box

theme = test_theme.TestTheme(config.default_theme)


class MainWindow(gtk.ApplicationWindow):
	
	def __init__(self, app, theme):
		gtk.Window.__init__(self, title="test", type=gtk.WindowType.TOPLEVEL, application=app)
		self.set_name("main_window")
		self.parent = app

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
		state = glib.Variant.new_boolean(self.is_fullscreen)
		self.parent.action_fullscreen.set_state(state)
		
		if self.is_fullscreen:
			self.unfullscreen()
			self.parent.header_bar.show()
			self.active_term.grab_focus()
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
			self.fullscreen()
			self.parent.header_bar.hide()
			self.set_focus(self.active_term)
			self.active_term.grab_focus()
		

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
