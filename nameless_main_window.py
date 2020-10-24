#from gi.repository import Gtk, Gdk, Keybinder, Wnck
from gi.repository import Gtk, Gdk
import nameless_config as config, nameless_main_box



class MainWindow(Gtk.ApplicationWindow):

	def __init__(self, app, theme):
		Gtk.Window.__init__(self, title="test", type=Gtk.WindowType.TOPLEVEL, application=app)
		self.set_name("main_window")
		self.parent = app

		self.connect("delete-event", Gtk.main_quit)
		self.connect("window-state-event", self.on_window_state_event)
		self.connect("focus-in-event", self.on_focus_in_event)
		self.connect("focus-out-event", self.on_focus_out_event)

		#self.wnck = Wnck.Screen.get_default()
		#self.wnck.force_update()
		#self.active_workspace = self.wnck.get_active_workspace()
		#self.last_active_workspace = self.wnck.get_active_workspace()

		self.is_present = True
		self.have_focus = True
		self.is_fullscreen = False

		self.theme = theme
		print("Theme used:", self.theme.theme_used)
		self.style_provider = Gtk.CssProvider()
		self.load_css(theme.css_file)

		self.bind_key()

		self.count_changed_state = 0

		self.main_box = nameless_main_box.TestMainBox(self, self.theme)

		self.add(self.main_box)
		self.active_term = self.main_box.active_term
		self.set_opacity(config.window_opacity)


	def load_css(self, css_file):

		css = open((css_file), 'rb')
		css_data = css.read()
		css.close()

		self.style_provider.load_from_data(css_data)

		Gtk.StyleContext.add_provider_for_screen(
			Gdk.Screen.get_default(), self.style_provider,
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)


	def on_focus_in_event(self, window, event):
#		print("Window is focused")
		self.have_focus = True


	def on_focus_out_event(self, window, event):
#		print("Window is not focused anymore")
		self.have_focus = False


	def bind_key(self):
		key_bind_hide = "Menu"
		#Keybinder.init()
		#Keybinder.bind(key_bind_hide, self.hide_app, "key_bind_hide: %s"% key_bind_hide)


	def hide_app(self, key_bind_hide, user_data):
		#self.last_event_time = Keybinder.get_current_event_time()
		#print ("Event time:", self.last_event_time)

		#self.wnck.force_update()
		#self.active_workspace = self.wnck.get_active_workspace()
#		print("Workspaces:", self.wnck.get_workspaces())
#		print("Active workspace:", self.active_workspace)
#		print("Last active workspace:", self.last_active_workspace)
#
		if self.is_present:
			print("Hiding app")
			if self.parent.is_drop_down:
				self.hide()
			else:
				self.iconify()
			self.is_present = False

		else:
			print("Showing app")
			if self.parent.is_drop_down:
				#if self.last_active_workspace != self.active_workspace:
				#	self.last_active_workspace = self.active_workspace
				#	self.hide()

				self.show()
#				self.present()
#				self.set_icon_from_file(config.file_program_icon)

			self.present_with_time(self.last_event_time)
			self.main_box.active_term.grab_focus()
			self.is_present = True


	def on_window_state_event(self, window, event):
		FOCUSED 	= Gdk.WindowState.FOCUSED
		TILED 		= Gdk.WindowState.TILED
		MAXIMIZED 	= Gdk.WindowState.MAXIMIZED
		ICONIFIED 	= Gdk.WindowState.ICONIFIED
		WITHDRAWN	= Gdk.WindowState.WITHDRAWN
		FULLSCREEN	= Gdk.WindowState.FULLSCREEN
		HIDDEN 		= "HIDDEN"
		DEICONIFIED	= "DEICONIFIED"
#		print("\nMASK:", event.changed_mask)
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

#		print("IS_PRESENT:", self.is_present)

		return True
