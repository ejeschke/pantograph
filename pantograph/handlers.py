import tornado.web
import tornado.websocket
import tornado.template
from tornado.ioloop import IOLoop

import random
import json
import os
import datetime
from collections import namedtuple

from . import templates

LOADER = tornado.template.Loader(os.path.dirname(templates.__file__))

class MainPageHandler(tornado.web.RequestHandler):
    def initialize(self, name, url):
        self.name = name
        self.url = url
    def get(self):
        t = LOADER.load("index.html")
        
        width = self.settings.get("canvasWidth", "fullWidth")
        height = self.settings.get("canvasHeight", "fullHeight")
        
        if self.name in self.settings:
            width = self.settings[self.name].get("canvasWidth", width)
            height = self.settings[self.name].get("canvasHeight", height)

        ws_url = os.path.join(self.url, "socket")
        
        self.write(t.generate(
            title = self.name, url = self.url, ws_url = ws_url,
            width = width, height = height))

DEFAULT_INTERVAL = 10

InputEvent = namedtuple("InputEvent", ["type", "x", "y", "button", 
                                       "alt_key", "ctrl_key", "meta_key",
                                       "shift_key", "key_code"])

class PantographHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, name):
        self.name = name
        interval = self.settings.get("timer_interval", DEFAULT_INTERVAL)
        if self.name in self.settings:
            interval = self.settings[self.name].get("timer_interval", interval)
        self.interval = interval
    
    def on_canvas_init(self, message):
        self.width = message["width"]
        self.height = message["height"]
        self.setup()
        self.draw("redraw")
        # randomize the first timeout so we don't get every timer
        # expiring at the same time
        interval = random.randint(1, self.interval)
        delta = datetime.timedelta(milliseconds = interval)
        self.timeout = IOLoop.current().add_timeout(delta, self.timer_tick)

    def on_close(self):
        IOLoop.current().remove_timeout(self.timeout)

    def on_message(self, raw_message):
        message = json.loads(raw_message)
        event_type = message.get("type")

        if event_type == "setbounds":
            self.on_canvas_init(message)
        else:
            event_callbacks = {
                "mousedown": self.on_mouse_down,
                "mouseup": self.on_mouse_up,
                "mousemove": self.on_mouse_move,
                "click": self.on_click,
                "dblclick": self.on_dbl_click,
                "keydown": self.on_key_down,
                "keyup": self.on_key_up,
                "keypress": self.on_key_press
            }
            event_callbacks[event_type](InputEvent(**message))

    def draw(self, operation, **kwargs):
        message = dict(kwargs)
        message['operation'] = operation
        raw_message = json.dumps(message)
        self.write_message(raw_message)

    def draw_rect(self, x, y, width, height, color = "#000", **extra):
        self.draw("drawRect", x=x, y=y, width=width, height=height, 
                              color=color, **extra)

    def fill_rect(self, x, y, width, height, color = "#000", **extra):
        self.draw("fillRect", x=x, y=y, width=width, height=height, 
                              color=color, **extra)

    def clear_rect(self, x, y, width, height, **extra):
        self.draw("clearRect", x=x, y=y, width=width, height=height,
                               **extra)
    
    def draw_oval(self, x, y, width, height, color = "#000", **extra):
        self.draw("drawOval", x=x, y=y, width=width, height=height, 
                              color=color, **extra)
    
    def fill_oval(self, x, y, width, height, color = "#000", **extra):
        self.draw("fillOval", x=x, y=y, width=width, height=height, 
                              color=color, **extra)

    def draw_circle(self, x, y, radius, color = "#000", **extra):
        self.draw("drawCircle", x=x, y=y, radius=radius, 
                                color=color, **extra)
    
    def fill_circle(self, x, y, radius, color = "#000", **extra):
        self.draw("fillCircle", x=x, y=y, radius=radius, 
                                color=color, **extra)

    def draw_line(self, startX, startY, endX, endY, color = "#000", **extra):
        self.draw("drawLine", startX=startX, startY=startY, 
                              endX=endX, endY=endY, color=color,
                              **extra)

    def fill_polygon(self, points, color = "#000", **extra):
        self.draw("fillPolygon", points=points, color=color, **extra)
    
    def draw_polygon(self, points, color = "#000", **extra):
        self.draw("drawPolygon", points=points, color=color, **extra)

    def draw_image(self, img_name, x, y, width=None, height=None, **extra):
        app_path = os.path.join("./images", img_name)
        handler_path = os.path.join("./images", self.name, img_name)

        if os.path.isfile(handler_path):
            img_src = os.path.join("/img", self.name, img_name)
        elif os.path.isfile(app_path):
            img_src = os.path.join("/img", img_name)
        else:
            raise FileNotFoundError("Could not find " + img_name)
        
        self.draw("drawImage", src=img_src, x=x, y=y, 
                               width=width, height=height,
                               **extra)


    def timer_tick(self):
        self.update()
        self.draw("redraw")
        delta = datetime.timedelta(milliseconds = self.interval)
        self.timeout = IOLoop.current().add_timeout(delta, self.timer_tick)

    def setup(self):
        pass

    def update(self):
        pass

    def on_mouse_down(self, event):
        pass

    def on_mouse_up(self, event):
        pass
    
    def on_mouse_move(self, event):
        pass

    def on_click(self, event):
        pass

    def on_dbl_click(self, event):
        pass

    def on_key_down(self, event):
        pass

    def on_key_up(self, event):
        pass

    def on_key_press(self, event):
        pass
