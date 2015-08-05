#! /usr/bin/python

from gi.repository import Gtk as gtk, Vte as vte, GLib as glib, Gdk as gdk, Gio as gio, Keybinder
import weakref
import signal
import sys
import os

default_shell 	= "/usr/bin/zsh"
default_width 	= 1000
default_height 	= 500

css_file 	= "test_vte.css"
theme_used 	= "solarized_dark"

nb_term = 0

terminal_list 	= []
active_term 	= 0
tab_list 		= []

window_opacity 		= 0.90
notebook_opacity 	= 0.95
terminal_opacity 	= 0.80
#window_opacity 	= 1
#notebook_opacity 	= 1
#terminal_opacity 	= 1
terminal_scrollback = 9999
terminal_encoding 	= "UTF-8"
terminal_scroll_output 	= True
terminal_scroll_key 	= True

FOCUSED 	= gdk.WindowState.FOCUSED
TILED 		= gdk.WindowState.TILED
MAXIMIZED 	= gdk.WindowState.MAXIMIZED
ICONIFIED 	= gdk.WindowState.ICONIFIED
WITHDRAWN	= gdk.WindowState.WITHDRAWN
HIDDEN 		= "HIDDEN"
DEICONIFIED	= "DEICONIFIED"


class TestTheme(object):
	
	def __init__(self, theme_name):

		c_base03 	= self.hex_to_RGBA("#002B36")
		c_base02 	= self.hex_to_RGBA("#073642")
		c_base01 	= self.hex_to_RGBA("#586e75")
		c_base00 	= self.hex_to_RGBA("#657b83")
		c_base0 	= self.hex_to_RGBA("#839496")
		c_base1 	= self.hex_to_RGBA("#93a1a1")
		c_base2 	= self.hex_to_RGBA("#eee8d5")
		c_base3 	= self.hex_to_RGBA("#fdf6e3")
		c_yellow 	= self.hex_to_RGBA("#b58900")
		c_orange 	= self.hex_to_RGBA("#cb4b16")
		c_red 		= self.hex_to_RGBA("#dc322f")
		c_magenta 	= self.hex_to_RGBA("#d33682")
		c_violet 	= self.hex_to_RGBA("#6c71c4")
		c_blue 		= self.hex_to_RGBA("#268bd2")
		c_cyan 		= self.hex_to_RGBA("#2aa198")
		c_green 	= self.hex_to_RGBA("#859900")

		if theme_name == "solarized_dark":
			self.palette = [c_base01, c_red, c_green, c_yellow, c_blue, c_magenta, c_cyan, c_base2, 
							c_base01, c_red, c_green, c_yellow, c_blue, c_magenta, c_cyan, c_base2]
			self.terminal_bg = c_base03
			self.terminal_fg = c_base0
			self.terminal_cursor = c_cyan
			self.terminal_highlight_bg = c_base0
			self.terminal_highlight_fg = c_base03
			
		elif theme_name == "solarized_light":
			self.palette = [c_base01, c_red, c_green, c_yellow, c_blue, c_magenta, c_cyan, c_base1, 
							c_base01, c_red, c_green, c_yellow, c_blue, c_magenta, c_cyan, c_base1]
			self.terminal_bg = c_base3
			self.terminal_fg = c_base00
			self.terminal_cursor = c_cyan
			self.terminal_highlight_bg = c_base00
			self.terminal_highlight_fg = c_base3

		self.terminal_bg_image = ""		
		self.terminal_cursor_shape = vte.CursorShape.UNDERLINE #Can be IBEAM or BLOCK 
		
	def hex_to_RGBA(self, hex_color):
		RGBA_color = gdk.RGBA()
		RGBA_color.parse(hex_color)
		RGBA_color.to_string()
		return RGBA_color

class TestMainBox(gtk.Box):
	
	def __init__(self):
		gtk.Box.__init__(self, orientation=gtk.Orientation.VERTICAL)
		gtk.StyleContext.add_class(self.get_style_context(), "linked")
		
		self.create_term_box()
		self.create_tool_box()

		self.active_tab = 0
		self.add_new_tab("Term")

		
	def create_term_box(self):
		self.term_box = TestTermBox(self)
		self.pack_start(self.term_box, True, True, 0)
	
	def create_tool_box(self):
		self.tool_box = TestToolBox(self)
		self.pack_end(self.tool_box, False, True, 0)
	
	def add_new_tab(self, tab_label):
		global nb_term
		self.term_box.add_term()
		self.tool_box.tab_box.add_tab(tab_label)
		nb_term = len(terminal_list)
		print("terminal_list:", terminal_list)
		print("tab_list:", tab_list)
		print("Lenght terminal_list:", len(terminal_list))
		print("Lenght tab_list:", len(tab_list))
		print("nb_term:", nb_term)
		self.set_term_active(nb_term)
		self.show_all()
			
	def set_term_active(self, nb_tab):
		global active_term
		print("a", self.active_tab, "b", nb_tab)
		if self.active_tab != nb_tab:
			i = 0
			for tab in tab_list:
				tab_list[i].set_name("tab_button")
				i += 1
			
			self.active_tab = nb_tab
			print("active_tab:", self.active_tab)
			tab_list[self.active_tab - 1].set_name("active_button")
			self.active_term = terminal_list[self.active_tab - 1]
			
			if nb_term > 1:
				print("Removing old terminal")
				self.term_box.destroy()
				self.create_term_box()
				
			print("New active term:", self.active_term)
			active_term = self.active_term

			self.term_box.add(self.active_term)
			self.show_all()
			active_term.grab_focus()

		
	
class TestTermBox(gtk.Box):
	
	def __init__(self, parent):
		gtk.Box.__init__(self, orientation=gtk.Orientation.HORIZONTAL)
#		gtk.Box.__init__(self)
		gtk.StyleContext.add_class(self.get_style_context(), "linked")
		self.set_name("term_box")
		self.parent = parent
		
	def add_term(self):
		global nb_term, terminal_list
		nb_term += 1
		self.term = TestTerminal()
		self.term.set_hexpand(True)
		self.term.grab_focus()
#		self.term.connect("child-exited", self.remove_term)
		terminal_list.append(self.term)

#	def remove_term(self, term, arg):
#		global nb_term, terminal_list
#		print(nb_term, "terminal remaining")
#		print("Removing active terminal")
#		nb_term -= 1
##		self.term.destroy()
#		print("Term list:", terminal_list)
#		i = 0
#		for term in terminal_list:
#			print("term:", term)
#			if self.term == term:
#				print("self:", self.term)
#				break
#			i += 1
#		print("i:", i)
#		terminal_list[i].destroy()
#		terminal_list.pop(i)
#		print("Term list:", terminal_list)
#		if nb_term <= 1: 
#			self.add_term()
#			self.show_all()


class TestToolBox(gtk.Box):
	
	def __init__(self, parent):
		gtk.Box.__init__(self, orientation=gtk.Orientation.HORIZONTAL)
		gtk.StyleContext.add_class(self.get_style_context(), "linked")
		self.set_name("tool_box")
		self.parent = parent
		
		self.create_tab_box()
		self.create_shortcut_box()
		
	def create_tab_box(self):
		self.tab_box = TestTabBox(self)
		self.pack_start(self.tab_box, True, True, 0)
		
	def create_shortcut_box(self):
		self.shortcut_box = TestShortcutBox(self)
		self.pack_end(self.shortcut_box, False, True, 0)
	



class TestTabBox(gtk.Box):
	
	def __init__(self, parent): 
		gtk.Box.__init__(self, orientation=gtk.Orientation.HORIZONTAL)
		gtk.StyleContext.add_class(self.get_style_context(), "linked")
		self.set_name("tab_box")
		self.parent = parent
		
#		self.tab_list = []
		
	def add_tab(self, tab_label):
		global tab_list
		self.button_tab = gtk.Button(tab_label)
		self.button_tab.connect("clicked", self.on_button_tab_clicked)
		tab_list.append(self.button_tab)
		self.add(self.button_tab)
		
	def remove_tab(self, tab_nb):
		self.remove(self.tab_list[tab_nb])
		
	def on_button_tab_clicked(self, widget):
		i = 0
		for tab in tab_list:
			if tab == widget:
				break
			i += 1
		self.parent.parent.set_term_active(i + 1)


class TestShortcutBox(gtk.Box):
	
	def __init__(self, parent): 
		gtk.Box.__init__(self, orientation=gtk.Orientation.HORIZONTAL)
		gtk.StyleContext.add_class(self.get_style_context(), "linked")
		self.set_name("shortcut_box")
		self.parent = parent
		
#		print("Parent:", parent)
		self.add_shortcuts()
		
	def add_shortcuts(self):
		self.button_new_tab = gtk.Button()
		icon = gio.ThemedIcon(name="tab-new-symbolic")
		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		self.button_new_tab.add(image)
		self.button_new_tab.connect("clicked", self.on_button_new_tab_clicked)
		self.add(self.button_new_tab)
	
	def on_button_new_tab_clicked(self, widget):
		print("New tab")
		self.parent.parent.add_new_tab(len(terminal_list))
		

class TestHeaderBar(gtk.Window):

	def __init__(self):
		gtk.Window.__init__(self, title="test", type=gtk.WindowType.TOPLEVEL)
#		self.set_default_size(default_width, default_height)
		hb = gtk.HeaderBar()
		hb.set_show_close_button(True)
		hb.props.title = "Test VTE 4"
		hb.set_name("header_bar")

		box_end = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
		gtk.StyleContext.add_class(box_end.get_style_context(), "linked")
		
		button_menu = gtk.Button()
		icon = gio.ThemedIcon(name="open-menu-symbolic")
		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		button_menu.add(image)
		button_menu.connect("clicked", self.on_button_menu_clicked)
		
		box_end.add(button_menu)
		hb.pack_end(box_end)
		
		self.set_titlebar(hb)
		self.main_box = TestMainBox()
		self.add(self.main_box)
		active_term.grab_focus()
		
	def on_button_menu_clicked(self, widget): 
		print("Menu clicked")
		self.main_box.term_box.remove_term(self.main_box.term_box.term, 0)
		self.show_all()

	
def hex_to_RGBA(hex_color):
	RGBA_color = gdk.RGBA()
	RGBA_color.parse(hex_color)
	RGBA_color.to_string()
	return RGBA_color


class TestTerminal(vte.Terminal):
	
	def __init__(self):
		vte.Terminal.__init__(self)
		self.set_name("terminal")
#		self.connect("child-exited", TestNotebook.remove_page)
		self.spawn_sync(
				vte.PtyFlags.DEFAULT,
				os.environ['HOME'],
				[default_shell],
				[],
				glib.SpawnFlags.DO_NOT_REAP_CHILD,
				None,
				None,
				)
		
		self.set_encoding(terminal_encoding)
		self.set_scrollback_lines(terminal_scrollback)
		self.set_scroll_on_output(terminal_scroll_output) 
		self.set_scroll_on_keystroke(terminal_scroll_key)
		
		self.theme = TestTheme(theme_used)

		self.set_colors(self.theme.terminal_fg, self.theme.terminal_bg, self.theme.palette)
		self.set_color_cursor(self.theme.terminal_cursor)
		self.set_cursor_shape(self.theme.terminal_cursor_shape)
#		self.set_color_highlight(self.theme.terminal_highlight_bg)
#		self.set_color_highlight_foreground(self.theme.terminal_highlight_fg)
		
		if self.theme.terminal_bg_image != "":
			self.set_background_image_file(self.theme.terminal_bg_image)  
		self.set_opacity(terminal_opacity)


class MainWindow(TestHeaderBar):
	
	def __init__(self):
		TestHeaderBar.__init__(self)
		self.set_name("main_window")
		self.set_default_size(default_width, default_height)
		self.connect("delete-event", gtk.main_quit)
		self.connect('window-state-event', self.on_window_state_event)
		self.connect('focus-in-event', self.on_focus_in_event)
		self.connect('focus-out-event', self.on_focus_out_event)
#		self.set_type_hint(gdk.WindowTypeHint.NORMAL)
		self.is_present = True
		self.have_focus = True
		self.load_css()
		self.bind_key()
		self.show_all()
		self.count_changed_state = 0
		self.last_count_changed_state = 0


	def on_focus_in_event(self, window, event):
		print("I'VE GOT FOCUS")
		self.have_focus = True
	
	def on_focus_out_event(self, window, event):
		print("FOCUS IS NOT HERE ANYMORE")
		self.have_focus = False
		
	
	def load_css(self):
		style_provider = gtk.CssProvider()

		css = open((css_file), 'rb') # rb needed for python 3 support
		css_data = css.read()
		css.close()

		style_provider.load_from_data(css_data)
		
		gtk.StyleContext.add_provider_for_screen(
			gdk.Screen.get_default(), style_provider,     
			gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)
	
	def bind_key(self):
		key_bind_hide = "Menu"
		Keybinder.init()
		Keybinder.bind(key_bind_hide, self.hide_app, "key_bind_hide: %s"% key_bind_hide)
		
	
	def hide_app(self, key_bind_hide, user_data):
		self.last_event_time = Keybinder.get_current_event_time()
		print ("Event time:", self.last_event_time)
		global active_term
#		print ("Handling", user_data)
#		print("SELF:", self)

		if self.is_present:
			print("Hiding app")
			self.iconify()
			self.is_present = False

		else:
			print("Showing app")
			self.present_with_time(self.last_event_time)
			active_term.grab_focus()
			self.is_present = True


	def on_window_state_event(self, window, event):
		self.count_changed_state += 1
		print("Count:", self.count_changed_state)
		print("Window state changed")
		print("Event changed_mask:", event.changed_mask)
		print("Event_state:", event.new_window_state)

		if self.is_active():
			print("Window is active")
			self.is_present = True
		
		if event.changed_mask & ICONIFIED:
			if event.new_window_state & ICONIFIED:
				print("WINDOW IS ICONIFIED")
				self.is_present = False
			elif event.new_window_state == 0:
				print("WINDOW IS DEICONIFIED")
				self.is_present = True
				
		elif event.changed_mask & (FOCUSED | TILED):
			if event.new_window_state == 0:
				print("WINDOW IS HIDDEN")
				self.is_present = False
			elif event.new_window_state & FOCUSED:
				print("WINDOW IS FOCUSED")
				self.is_present = True
			elif event.new_window_state & TILED:
				print("WINDOW IS HIDDEN")
				self.is_present = False
				
		if event.changed_mask & WITHDRAWN:
			if event.new_window_state & WITHDRAWN:
				print("WINDOW IS WITHDRAWN")
				self.is_present = False

		active_term.grab_focus()
		self.set_focus(active_term)
		return True
			

def signal_handler(signal_rcv, frame):
	print("PID of application:", os.getpid())
	print("SIGNAL:", signal_rcv)
	os.killpg(os.getpid(), signal.SIGTERM)
#	gtk.main_quit()

	

if __name__ == "__main__":
#	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	MainWindow()
	gtk.main()
	
	
