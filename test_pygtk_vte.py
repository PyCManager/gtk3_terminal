#! /usr/bin/python

from gi.repository import Gtk as gtk, Vte as vte, GLib as glib, Gdk as gdk, Gio as gio
#import pango
import sys
import os

default_shell = "/usr/bin/zsh"
default_width = 880
default_height = 440

window_opacity = 0.90
notebook_opacity = 0.95
terminal_opacity = 0.80
#window_opacity = 1
#notebook_opacity = 1
#terminal_opacity = 1
terminal_scrollback = 9999

TOP = gtk.PositionType.TOP
RIGHT = gtk.PositionType.RIGHT
BOTTOM = gtk.PositionType.BOTTOM
LEFT = gtk.PositionType.LEFT

nb_pages = 1

class HeaderBarWindow(gtk.Window):

	def __init__(self):
#		window = HeaderBarWindow()
		gtk.Window.__init__(self, title="TEST")
#		self.set_border_width(10)
		self.set_default_size(default_width, default_height)

		hb = gtk.HeaderBar()
		hb.set_show_close_button(True)
		hb.props.title = "Test VTE 3"
		self.set_titlebar(hb)

		button_menu = gtk.Button()
		icon = gio.ThemedIcon(name="view-sidebar-symbolic")
		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		button_menu.add(image)
		button_menu.connect("clicked", self.on_button_menu_clicked)

		box = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
		gtk.StyleContext.add_class(box.get_style_context(), "linked")

		button_new_tab = gtk.Button()
		icon = gio.ThemedIcon(name="tab-new-symbolic")
		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		button_new_tab.add(image)
#		button_new_tab.connect("clicked", self.on_button_new_tab_clicked)
		box.add(button_new_tab)

		button_stop_process = gtk.Button()
		icon = gio.ThemedIcon(name="process-stop-symbolic")
		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		button_stop_process.add(image)
#		button_stop_process.connect("clicked", self.on_button_stop_process_clicked)
		box.add(button_stop_process)

		hb.pack_start(box)
		hb.pack_end(button_menu)
		
#		self.add(gtk.Box)
		self.add(TestBox())		
		
#		self.main_box = TestMainBox()
#		self.add(self.main_box)
	
	def on_button_menu_clicked(self, widget): 
		print("Menu clicked")

#	def on_button_new_tab_clicked(self, widget): 
#		print("New tab clicked")
#		global window
#		self.notebook.add_page(str(nb_pages))
#		self.show_all()

#	def on_button_stop_process_clicked(self, widget): 
#		print("Stop process clicked")


class TestBox(gtk.Box):
	
	def __init__(self):
		gtk.Box.__init__(self, orientation=gtk.Orientation.HORIZONTAL)
		gtk.StyleContext.add_class(self.get_style_context(), "linked")
		
		self.notebook = TestNotebook("Term")
		self.notebook.add_page(str(nb_pages))
#		self.notebook.add_page(str(nb_pages))
		self.notebook.set_opacity(notebook_opacity)
		
		self.pack_end(self.notebook, True, True, 0)
#		print("Notebook:", self.notebook)
		self.execbox = TestExecBox(self.notebook)
		self.pack_start(self.execbox, False, True, 0)	
#		self.show_all()

class TestExecBox(gtk.Box):
	
	def __init__(self, notebook):
		gtk.Box.__init__(self, orientation=gtk.Orientation.VERTICAL)
		gtk.StyleContext.add_class(self.get_style_context(), "linked")
		
		self.notebook = notebook
		print("NOTEBOOK:", self.notebook)
		button_new_tab = gtk.Button()
		icon = gio.ThemedIcon(name="tab-new-symbolic")
		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		button_new_tab.add(image)
		button_new_tab.connect("clicked", self.on_button_new_tab_clicked)
		self.add(button_new_tab)

		button_quit_terminal = gtk.Button()
		icon = gio.ThemedIcon(name="edit-delete-symbolic")
		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		button_quit_terminal.add(image)
		button_quit_terminal.connect("clicked", self.on_button_quit_terminal_clicked)
		self.add(button_quit_terminal)

		button_stop_process = gtk.Button()
		icon = gio.ThemedIcon(name="process-stop-symbolic")
		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		button_stop_process.add(image)
		button_stop_process.connect("clicked", self.on_button_stop_process_clicked)
		self.add(button_stop_process)
		
		button_clear_terminal = gtk.Button()
		icon = gio.ThemedIcon(name="edit-clear-symbolic")
		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		button_clear_terminal.add(image)
		button_clear_terminal.connect("clicked", self.on_button_clear_terminal_clicked)
		self.add(button_clear_terminal)
		
		button_fullscreen = gtk.Button()
		icon = gio.ThemedIcon(name="view-fullscreen-symbolic")
		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		button_fullscreen.add(image)
		button_fullscreen.connect("clicked", self.on_button_fullscreen_clicked)
		self.add(button_fullscreen)
		
		button_restore_screen = gtk.Button()
		icon = gio.ThemedIcon(name="view-restore-symbolic")
		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		button_restore_screen.add(image)
		button_restore_screen.connect("clicked", self.on_button_restore_screen_clicked)
		self.add(button_restore_screen)
		
		button_toggle_titlebar = gtk.Button()
		icon = gio.ThemedIcon(name="focus-top-bar-symbolic")
		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		button_toggle_titlebar.add(image)
		button_toggle_titlebar.connect("clicked", self.on_button_toggle_titlebar_clicked)
		self.add(button_toggle_titlebar)
		
		button_quit = gtk.Button()
		icon = gio.ThemedIcon(name="window-close-symbolic")
		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		button_quit.add(image)
		button_quit.connect("clicked", self.on_button_quit_clicked)
		self.pack_end(button_quit, False, True, 0)
		
		
		
	def on_button_new_tab_clicked(self, widget):
		print("New tab")
#		global nb_pages
		print("NOTEBOOK=:", self.notebook)
#		nb_pages += 1
		self.notebook.add_page(str(nb_pages))
		self.show_all()
	
	def on_button_stop_process_clicked(self, widget):
		print("Stop process")
	
	def on_button_quit_clicked(self, widget):
		print("Quitting application")
		gtk.main_quit()

	def on_button_clear_terminal_clicked(self, widget):
		print("Clearing terminal")
	
	def on_button_quit_terminal_clicked(self, widget):
		print("Quitting terminal")
	
	def on_button_fullscreen_clicked(self, widget):
		print("Fullscreen")
	
	def on_button_restore_screen_clicked(self, widget):
		print("Restoring window")

	def on_button_toggle_titlebar_clicked(self, widget):
		print("Toggling titlebar")
		
#class TestMainBox(gtk.Box):
#	
#	def __init__(self):
##		gtk.VBox.__init__(self)
#		gtk.Box.__init__(self, orientation=gtk.Orientation.VERTICAL)
#		gtk.StyleContext.add_class(self.get_style_context(), "linked")
#		

#		terminal_part = gtk.ScrolledWindow()
#		terminal_part.add(TestTerminal())
##		pack_start(child, expand=True, fill=True, padding=0)
#		self.pack_start(terminal_part, True, True, 0)

##		button_new_tab2 = gtk.Button()
##		icon = gio.ThemedIcon(name="tab-new-symbolic")
##		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
##		button_new_tab2.add(image)
##		button_new_tab2.connect("clicked", self.on_button_new_tab2_clicked)
#		tab_part = TestTabBox()
#		self.pack_end(tab_part, False, True, 0)


#class TestTabBox(gtk.Box):
#	
#	def __init__(self):
#		gtk.Box.__init__(self, orientation=gtk.Orientation.HORIZONTAL)
#		gtk.StyleContext.add_class(self.get_style_context(), "linked")
#		
#		self.add_tab("Term")

#		button_new_tab = gtk.Button()
#		icon = gio.ThemedIcon(name="tab-new-symbolic")
#		image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
#		button_new_tab.add(image)
#		button_new_tab.connect("clicked", self.on_button_new_tab_clicked)
#		self.pack_end(button_new_tab, False, True, 0)		
#				
#	def add_tab(self, tab_label):
#		global nb_pages
#		nb_pages += 1
#		button = gtk.Button(tab_label)
#		self.pack_start(button, False, True, 0)
#		
#	def on_button_new_tab_clicked(self, widget): 
#		print("New tab clicked")
#		self.add_tab(str(nb_pages))
#		self.show_all()
		
class TestNotebook(gtk.Notebook):

	def __init__(self, page_label):
		gtk.Notebook.__init__(self)
		self.set_tab_pos(BOTTOM)
		self.pages = []
		self.add_page(page_label)
	
	def add_page(self, page_label):
		global nb_pages
		nb_pages += 1
#		page = TestTerminal()
		page = gtk.ScrolledWindow()
		page.add(TestTerminal())
		self.pages.append(page)
#		print("PAGES", self.pages)
		print("NB PAGES: ", nb_pages)
		self.append_page(page, gtk.Label(page_label))
		self.set_tab_reorderable(page, True)
		self.show_all()

	def remove_page(self, a):
#		print(self)
		global nb_pages
		nb_pages -= 1
		if nb_pages > 1:
			print("Closing a page")
			print("Remaining pages:", nb_pages - 1)
			self.destroy()
		else:
			print("Closing application")
			gtk.main_quit()


class TestTerminal(vte.Terminal):

	def __init__(self):
		vte.Terminal.__init__(self)
		self.connect("child-exited", TestNotebook.remove_page)
		self.spawn_sync(
				vte.PtyFlags.DEFAULT,
				os.environ['HOME'],
				[default_shell],
				[],
				glib.SpawnFlags.DO_NOT_REAP_CHILD,
				None,
				None,
				)
		self.set_encoding("UTF-8")
		self.set_scrollback_lines(9999)
		self.set_opacity(terminal_opacity)
		
#		font = pango.FontDescription()
#		font.set_family("Ubuntu Mono")

#		font.set_size(11 * pango.SCALE)
#		font.set_weight(pango.WEIGHT_NORMAL)
#		font.set_stretch(pango.STRETCH_NORMAL)
#		
#		self.set_font(font, True)



class MainWindow(HeaderBarWindow):
	
	def __init__(self):
#		window = HeaderBarWindow()
		HeaderBarWindow.__init__(self)
		self.connect("delete-event", gtk.main_quit)
		self.set_opacity(window_opacity)
		self.show_all()


if __name__ == "__main__":
	MainWindow()
	gtk.main()
