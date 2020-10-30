from gi.repository import Gtk, Vte, GLib
import nameless_config as config
import os



class TestTermBox(Gtk.Box):

	def __init__(self, parent, theme):
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
		Gtk.StyleContext.add_class(self.get_style_context(), "linked")

		self.set_name("term_box")
		self.parent = parent

		self.theme = theme
		self.scroll_window_term = Gtk.ScrolledWindow()
		self.scroll_window_term.set_name("scroll_window_term")
		self.scroll_window_term.set_shadow_type(Gtk.ShadowType.NONE)
		self.scroll_window_term.set_overlay_scrolling(False)

		self.create_scroll_box_term()
		self.pack_end(self.scroll_box_term, False, False, 0)
		self.show_all()

	def create_scroll_box_term(self):
		self.scroll_box_term = Gtk.Box()


	def create_term(self, terminal_list, path_open_terminal):

		self.term = TestTerminal(self.theme, path_open_terminal)
		self.term.set_hexpand(True)
		self.term.set_vexpand(True)

		if config.launch_command_new_term:
			command = config.launch_command_new_term
			length_command = len(command)
			self.term.feed_child(command, length_command)
		#print("DIR_TERMINAL:", dir(self.term))
		self.term.grab_focus()
		terminal_list.append(self.term)

		return terminal_list



class TestTerminal(Vte.Terminal):

	def __init__(self, theme, path_open_terminal):
		Vte.Terminal.__init__(self)
		self.set_name("terminal")
		self.pid = self.spawn_sync(
				Vte.PtyFlags.DEFAULT,
				path_open_terminal,
				[config.default_shell],
				[],
				GLib.SpawnFlags.DO_NOT_REAP_CHILD,
				None,
				None,
				)

		self.set_encoding(config.terminal_encoding)
		self.set_scrollback_lines(config.terminal_scrollback)
		self.set_scroll_on_output(config.terminal_scroll_output)
		self.set_scroll_on_keystroke(config.terminal_scroll_key)
		self.set_mouse_autohide(config.terminal_mouse_autohide)

#		if theme.theme_used != "default":
		self.set_colors(theme.terminal_fg, theme.terminal_bg, theme.palette)
		self.set_color_cursor(theme.terminal_cursor)
		self.set_cursor_shape(theme.terminal_cursor_shape)


		if theme.terminal_bg_image != "":
			self.set_background_image_file(theme.terminal_bg_image)


