from gi.repository import Gtk as gtk
import nameless_config as config



class TestToolBox(gtk.Box):
	
	def __init__(self, parent, theme):
		gtk.Box.__init__(self, orientation=gtk.Orientation.HORIZONTAL)
		gtk.StyleContext.add_class(self.get_style_context(), "linked")
		self.set_name("tool_box")
		self.parent = parent
		self.theme = theme
		
		self.count_scroll_up = 0
		self.count_scroll_down = 0
		
		self.create_tab_box()

		
	def create_tab_box(self):
		self.tab_box = TestTabBox(self, self.theme)
		self.tab_box.set_spacing(config.spacing_button_tab_box)

		self.scroll_window_tab = gtk.ScrolledWindow()
		self.scroll_window_tab.set_name("scroll_window_tab")

		self.scroll_window_tab.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.NEVER)
		hsb = self.scroll_window_tab.get_hscrollbar()
		if not config.show_tab_hscrollbar:
			hsb.hide()
			
		self.scroll_window_tab.add(self.tab_box)
		self.scroll_window_tab.set_shadow_type(gtk.ShadowType.NONE)
#		Remove shadow from viewport child to make a small 1px border disappear
		for child in self.scroll_window_tab.get_children():
			child.set_shadow_type(gtk.ShadowType.NONE)

		self.event_tab_box = gtk.EventBox()
		self.event_tab_box.set_name("event_tab_box")
		self.event_tab_box.set_hexpand(True)
		self.event_tab_box.connect("scroll-event", self.on_scroll_event)
		self.event_tab_box.connect("button-press-event", self.on_button_press_event)
		self.event_tab_box.add(self.scroll_window_tab)
		
#		self.parent.set_border_width(config.width_tab_box_border)
#		self.event_tab_box.set_border_width(config.width_tab_box_border)
		self.scroll_window_tab.set_border_width(config.width_tab_box_border)
#		self.tab_box.set_border_width(config.width_tab_box_border)

		if config.tab_box_pack_start:
			self.pack_start(self.event_tab_box, True, True, 0)
		else:
			self.pack_end(self.event_tab_box, True, True, 0)


	def on_button_press_event(self, widget, event):
		print("Click detected")
		print("Button:", event.button)
		button_clicked = event.button
		event_window = event.window
		event_window_children = event_window.get_children()
		self.tab_list = self.parent.tab_list
		self.nb_terminals = self.parent.nb_terminals
		
		if event_window_children:
			print("Click on tab box")
			if button_clicked == config.button_open_term:
				print("Opening new tab from button:", config.button_open_term)
				self.parent.add_new_term(self.nb_terminals)
		else:
			print("Click on tab button")
			if button_clicked == config.button_close_term:
				print("Closing selected from button:", config.button_close_term)
				i = 0
				for tab in self.tab_list:
					if tab.get_event_window() == event_window:
						print("nb tab clicked:", i)
						self.parent.remove_term(i, True)				
					else:
						i += 1
				
	
	def on_scroll_event(self, widget, event):
		
		if event.delta_x > event.delta_y: 
			self.count_scroll_up += 1
			if self.count_scroll_up >= config.sensibility_scroll:
				print("GOING UP")
				self.parent.move_next_term()
				self.count_scroll_up = 0
		
		elif event.delta_x < event.delta_y: 
			self.count_scroll_down += 1
			if self.count_scroll_down >= config.sensibility_scroll:
				print("GOING DOWN")
				self.parent.move_prev_term()
				self.count_scroll_down = 0
				

	


class TestTabBox(gtk.Box):
	
	def __init__(self, parent, theme): 
		gtk.Box.__init__(self, orientation=gtk.Orientation.HORIZONTAL)
		gtk.StyleContext.add_class(self.get_style_context(), "linked")
		self.set_name("tab_box")
		self.parent = parent
		self.theme = theme
		
		
	def add_tab(self, tab_label, tab_list):
		self.button_tab = gtk.Button(tab_label)
		tab_list.append(self.button_tab)
		self.button_tab.connect("clicked", self.on_button_tab_clicked, tab_list)

		self.button_tab.set_relief(gtk.ReliefStyle.NONE)
		self.add(self.button_tab)
		
		return tab_list


	def remove_tab(self, tab_nb, tab_list):
		self.scroll_window.remove(tab_list[tab_nb])
	
		
	def on_button_tab_clicked(self, widget, tab_list):
		i = 0
		for tab in tab_list:
			if tab == widget:
				break
			i += 1
		self.parent.parent.set_term_active(i)		


