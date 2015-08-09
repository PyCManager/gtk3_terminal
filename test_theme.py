from gi.repository import Gtk as gtk, Gdk as gdk, Gio as gio, Vte as vte
import test_config as config


path_to_css = config.path_to_css
path_to_icons = config.path_to_icons

icon_dict = { 	"new_term" : "tab-new-symbolic", 
				"close_term" : "edit-delete-symbolic",
				"header_menu" : "open-menu-symbolic",
				"tab_menu" : "open-menu-symbolic"}



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
		self.theme_used = theme_name
		
				
		if theme_name == "default":
			print("Using default theme")
			self.relief_button_shortcut_box = gtk.ReliefStyle.NORMAL
			self.relief_button_tab_box = gtk.ReliefStyle.NORMAL
		
		elif theme_name == "solarized_dark":
			self.palette = [c_base01, c_red, c_green, c_yellow, c_blue, c_magenta, c_cyan, c_base2, 
							c_base01, c_red, c_green, c_yellow, c_blue, c_magenta, c_cyan, c_base2]
			self.terminal_bg = c_base03
			self.terminal_fg = c_base0
			self.terminal_cursor = c_cyan
			self.terminal_highlight_bg = c_base0
			self.terminal_highlight_fg = c_base03
			icon_dict["new_term"] = "new_term_solarized_dark"
			icon_dict["close_term"] = "close_term_solarized_dark"
#			icon_dict["header_menu"] = "header_menu_solarized_dark"
			icon_dict["tab_menu"] = "tab_menu_solarized_dark"
			self.relief_button_shortcut_box = gtk.ReliefStyle.NONE
			self.relief_button_tab_box = gtk.ReliefStyle.NONE
			
		elif theme_name == "solarized_light":
			self.palette = [c_base01, c_red, c_green, c_yellow, c_blue, c_magenta, c_cyan, c_base1, 
							c_base01, c_red, c_green, c_yellow, c_blue, c_magenta, c_cyan, c_base1]
			self.terminal_bg = c_base3
			self.terminal_fg = c_base00
			self.terminal_cursor = c_cyan
			self.terminal_highlight_bg = c_base00
			self.terminal_highlight_fg = c_base3
			self.relief_button_shortcut_box = gtk.ReliefStyle.NONE
			self.relief_button_tab_box = gtk.ReliefStyle.NONE
#			icon_dict["new_term"] = "new_term_solarized_dark"
#			icon_dict["close_term"] = "close_term_solarized_dark"
#			icon_dict["header_menu"] = "header_menu_solarized_dark"

		self.terminal_bg_image = ""		
		self.terminal_cursor_shape = vte.CursorShape.UNDERLINE #Can be IBEAM or BLOCK
		
		self.css_file = path_to_css + theme_name + ".css"
		
		
	def hex_to_RGBA(self, hex_color):
		RGBA_color = gdk.RGBA()
		RGBA_color.parse(hex_color)
		RGBA_color.to_string()
		return RGBA_color
	
	
	def get_image(self, image_name):
	
		if self.theme_used == "default":
			image_name = icon_dict[image_name]
			icon = gio.ThemedIcon(name=image_name)
			image = gtk.Image.new_from_gicon(icon, gtk.IconSize.BUTTON)
		else:
			image_name = path_to_icons + icon_dict[image_name] + ".svg"
			try:
				image = gtk.Image.new_from_file(image_name)
			except Exception:
				print("Exception opening file:", image_name)
		
		return image

		
