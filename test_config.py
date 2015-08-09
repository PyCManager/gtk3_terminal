import test_theme
from os.path import expanduser


name_application = "Nameless terminal"
default_shell 	= "/usr/bin/zsh"
theme_list = [ "default", "solarized_dark", "solarized_light" ]
default_theme 	= theme_list[1]

path_to_css = "./themes/"
path_to_icons = "./icons/"
file_window_state = "./config/window_state"

window_default_width 	= 1000
window_default_height 	= 500
window_opacity 		= 0.90
window_restore_state = True
#window_opacity 	= 1

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


shortcut_dict = {	"<Alt>Up" : "accel_new_term", "<Control>T" : "accel_new_term",
					"<Alt>Left" : "accel_prev_term", "<Alt>Right" : "accel_next_term"}

terminal_scrollback	= 9999
terminal_encoding	= "UTF-8"
terminal_scroll_output 	= True
terminal_scroll_key 	= True
terminal_default_path 	= expanduser("~")
terminal_print_working_dir_path = False
terminal_print_working_dir = True
terminal_open_tab_working_dir = True
terminal_deleted_activate_prev = True
terminal_mouse_autohide = True

#Cleaning is a hack to hide a white 1px bar around tool_box when using a dark theme
launch_command_new_term = "clear\n"

