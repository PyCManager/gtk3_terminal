from gi.repository import Gtk as gtk, Gdk as gdk, Gio as gio
import test_config as config
import os

path_to_css = config.path_to_css
path_to_icons = config.path_to_icons

icon_dict = { 	"new_term" 		: "tab-new-symbolic", 
				"close_term" 	: "edit-delete-symbolic",
				"header_menu" 	: "open-menu-symbolic",
				"tab_menu" 		: "open-menu-symbolic",
				"fullscreen" 	: "view-fullscreen-symbolic",
				"preferences" 	: "system-run-symbolic",
				"night_mode" 	: "object-inverse",
				"go_home" 		: "go-home-symbolic",
				"exit_app" 		: "window-close-symbolic",
				"drop_down" 	: "go-top-symbolic"}



class TestTheme(object):
	
	def __init__(self, theme_name):
		global icon_dict

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
		c_black 	= self.hex_to_RGBA("#000000")
		c_white 	= self.hex_to_RGBA("#ffffff")
		
		self.theme_used = theme_name
		
		self.c_1 = c_base01
		self.c_2 = c_red
		self.c_3 = c_green
		self.c_4 = c_yellow
		self.c_5 = c_blue
		self.c_6 = c_magenta
		self.c_7 = c_cyan
		self.c_8 = c_base2
		
		self.terminal_bg = c_black
		self.terminal_fg = c_white
		self.terminal_cursor = c_white
				
		if theme_name == "default":
			print("Using default theme")
			self.relief_button_shortcut_box = gtk.ReliefStyle.NORMAL
			self.relief_button_tab_box = gtk.ReliefStyle.NORMAL
			self.relief_button_main_menu = gtk.ReliefStyle.NORMAL
		
		elif theme_name == "solarized_dark" or theme_name == "debug":
			self.c_1 = c_base01
			self.c_8 = c_base2
			
			self.terminal_bg = c_base03
			self.terminal_fg = c_base0
			self.terminal_cursor = c_cyan
			
			path_theme = theme_name + "/"

			for icon_name in icon_dict:
				icon_dict[icon_name] = path_theme + icon_name

			self.relief_button_shortcut_box = gtk.ReliefStyle.NONE
			self.relief_button_tab_box = gtk.ReliefStyle.NONE
			self.relief_button_main_menu = gtk.ReliefStyle.NONE
			
		elif theme_name == "solarized_light":
			self.c_1 = c_base01
			self.c_8 = c_base1

			self.terminal_bg = c_base3
			self.terminal_fg = c_base00
			self.terminal_cursor = c_cyan
			
			path_theme = theme_name + "/"
			
			for icon_name in icon_dict:
				icon_dict[icon_name] = path_theme + icon_name
			
			self.relief_button_shortcut_box = gtk.ReliefStyle.NONE
			self.relief_button_tab_box = gtk.ReliefStyle.NONE
			self.relief_button_main_menu = gtk.ReliefStyle.NONE
			

		self.palette = [self.c_1, self.c_2, self.c_3, self.c_4, self.c_5, self.c_6, self.c_7, self.c_8, 
						self.c_1, self.c_2, self.c_3, self.c_4, self.c_5, self.c_6, self.c_7, self.c_8]

		self.terminal_bg_image = config.terminal_bg_image
		self.terminal_cursor_shape = config.terminal_cursor_shape
		
		self.css_file = path_to_css + theme_name + ".css"
		
	
	def load_icons(self, app):
#		TODO: Do this in loop.
	
		image = self.get_image("fullscreen")
		app.button_fullscreen.get_child().destroy()
		app.button_fullscreen.add(image)
		app.button_fullscreen.show_all()
		
		image = self.get_image("night_mode")
		app.button_night_mode.get_child().destroy()
		app.button_night_mode.add(image)
		app.button_night_mode.show_all()

		image = self.get_image("header_menu")
		app.button_header_menu.get_child().destroy()
		app.button_header_menu.add(image)
		app.button_header_menu.show_all()
		
		image = self.get_image("exit_app")
		app.button_exit_app.get_child().destroy()
		app.button_exit_app.add(image)
		app.button_exit_app.show_all()
		
		image = self.get_image("new_term")
		app.button_new_term.get_child().destroy()
		app.button_new_term.add(image)
		app.button_new_term.show_all()
		
		image = self.get_image("close_term")
		app.button_close_term.get_child().destroy()
		app.button_close_term.add(image)
		app.button_close_term.show_all()
		
		image = self.get_image("drop_down")
		app.button_drop_down.get_child().destroy()
		app.button_drop_down.add(image)
		app.button_drop_down.show_all()
	
		
	def hex_to_RGBA(self, hex_color):
		RGBA_color = gdk.RGBA()
		RGBA_color.parse(hex_color)
		RGBA_color.to_string()
		return RGBA_color
	
	
	def get_image(self, image_name):
		image_path = path_to_icons + icon_dict[image_name] + ".svg"
#		print("IMG PATH:", image_path)
		if os.path.isfile(image_path):
			try:
				image = gtk.Image.new_from_file(image_path)
			except Exception:
				print("Exception opening file:", image_path)
		else:
			image_name = icon_dict[image_name]
			icon = gio.ThemedIcon(name=image_name)
			image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		
		return image
		
		

		
