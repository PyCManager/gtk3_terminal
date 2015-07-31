#! /usr/bin/python

from gi.repository import Gtk as gtk, Vte as vte, GLib as glib, Gdk as gdk, Gio as gio, Keybinder
import weakref
import sys
import os

default_shell = "/usr/bin/zsh"
default_width = 1000
default_height = 500

css_file = 'test_vte.css'

nb_term = 0

terminal_list = []
tab_list = []

class TestMainBox(gtk.Box):
	
	def __init__(self):
		gtk.Box.__init__(self, orientation=gtk.Orientation.VERTICAL)
		gtk.StyleContext.add_class(self.get_style_context(), "linked")
		
		self.create_term_box()
		self.create_tool_box()
#		self.term_box.new_term()
#		self.add_new_term("Terminal")
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
#				self.term_box.remove(self.active_term)
				self.term_box.destroy()
				self.create_term_box()
#				self.tool_box.tab_box.add_tab(str(self.active_tab))
#			else:
			print("New active term:", self.active_term)
#			self.term_box.add_term(self.active_term)
			self.term_box.add(self.active_term)
			self.show_all()
#			print("FOCUS:",self.term_box.term.has_focus())
#			self.term_box.grab_focus()
#			self.set_focus(self.term_box.term)
#			self.term_box.set_accept_focus(True)
		
	
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
#		self.grab_focus()
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
#		self.parent.parent.set_term_active(len(terminal_list) - 1)

		
		

class TestHeaderBar(gtk.Window):

	def __init__(self):
		gtk.Window.__init__(self, title="test")
#		self.set_default_size(default_width, default_height)
#		self.set_accept_focus(True)
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
		self.set_focus(self.main_box.term_box.term)
		
	def on_button_menu_clicked(self, widget): 
		print("Menu clicked")
		self.main_box.term_box.remove_term(self.main_box.term_box.term, 0)
		self.show_all()
		
		


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


class MainWindow(TestHeaderBar):
	
	def __init__(self):
		TestHeaderBar.__init__(self)
		self.connect("delete-event", gtk.main_quit)
		self.set_name("main_window")
		self.set_default_size(default_width, default_height)
		self.is_present = True
		style_provider = gtk.CssProvider()

		css = open((css_file), 'rb') # rb needed for python 3 support
		css_data = css.read()
		css.close()

		style_provider.load_from_data(css_data)

		gtk.StyleContext.add_provider_for_screen(
			gdk.Screen.get_default(), style_provider,     
			gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)
		
		self.show_all()
		self.main_box.term_box.term.grab_focus()
		self.set_focus(self.main_box.term_box.term)
		
		keystr = "Menu"
		Keybinder.init()
		Keybinder.bind(keystr, self.callback, "keystring %s (user data)" % keystr)
		print ("Press", keystr, "to handle keybinding and quit")
	
	def callback(self, keystr, user_data):
		print ("Handling", user_data)
		print ("Event time:", Keybinder.get_current_event_time())
		if self.is_present:
			self.iconify()
			self.is_present = False
		else:
			self.present()
			self.is_present = True


if __name__ == "__main__":
	MainWindow()
	gtk.main()
	
	
