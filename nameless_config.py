from gi.repository import Gtk as gtk, Vte as vte
from os.path import expanduser
#import nameless_theme
import logging

logging_level = logging.DEBUG
rename_application = True
title_application = "Nameless terminal"
subtitle_application = "Version 0.99"
path_in_subtitle = True
default_shell 	= "/usr/bin/zsh"
theme_list = [ "default", "solarized_dark", "solarized_light", "debug" ]
default_theme = theme_list[1]
restore_night_mode = True
night_mode_state = True

path_to_css = "themes/"
path_to_icons = "icons/"
name_program_icon = "nameless_term_home.svg"
file_program_icon = path_to_icons + name_program_icon
file_window_state = "config/window_state"
file_config = "nameless_config.py"
file_ui_main_window = "ui/main_window.ui"
file_ui_header_bar = "ui/header_bar.ui"
file_ui_popover_menu = "ui/popover_menu.ui"
file_ui_theme_submenu = "ui/theme_submenu.ui"
file_ui_tool_box = "ui/tool_box.ui"
file_ui_shortcut_box = "ui/shortcut_box.ui"


delimiter = " = "

window_default_width = 1000
window_default_height = 500
window_opacity = 0.90
window_restore_state = True
window_state = [(553, 206), (877, 421)]
is_drop_down = True
drop_down_state = [(-17, 13), (1634, 534)]
drop_down_default_position = [-42, -42]
drop_down_default_size = [9999, 34]
count_resize_event_max = 3
#There is a bug. My screen is detected as 1600x900 (as it should be). But I have in fact 1634px in width...
free_width_pixel = 34
#window_opacity 	= 1
main_menu_opacity = 0.90
main_menu_halign = gtk.Align.CENTER
main_menu_show_icons = True
override_menu_relief = False

show_close_button = True
show_tab_hscrollbar = False

width_tab_box_border = 6
width_shortcut_box_border = 6
width_tab_border = 6
spacing_button_tab_box = 6
tab_box_pack_start = True

button_open_term = 2
button_close_term = 2
sensibility_scroll = 4

					
shortcut_dict = {	"app.new_term" : ["<Alt>Up", "<Ctrl>T"], "app.drop_down" : ["<Alt>Down"],
					"app.prev_term" : ["<Alt>Left"], "app.next_term" : ["<Alt>Right"],
					 "app.fullscreen" : ["F11"],
					 "app.copy_clipboard" : ["<Ctrl><Shift>C"], "app.paste_clipboard" : ["<Ctrl><Shift>V"]}

terminal_scrollback	= 9999
terminal_encoding = "UTF-8"
terminal_scroll_output = True
terminal_scroll_key = True
terminal_default_path = expanduser("~")
terminal_print_working_dir_path = False
terminal_print_working_dir = True
terminal_open_tab_working_dir = True
terminal_deleted_activate_prev = True
terminal_mouse_autohide = True
terminal_bg_image = ""
#Can be IBEAM or BLOCK
terminal_cursor_shape = vte.CursorShape.UNDERLINE
terminal_default_name = "Terminal"

#Cleaning is a hack to hide a white 1px bar around tool_box when using a dark theme
#launch_command_new_term = "clear\n"
launch_command_new_term = ""
