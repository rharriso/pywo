#
# PyWO - Python Window Organizer
# Copyright 2010, Wojciech 'KosciaK' Pietrzok
#
# This file is part of PyWO.
#
# PyWO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyWO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyWO.  If not, see <http://www.gnu.org/licenses/>.
#

"""Listen for events generated by X Server and dispatch them to handlers."""

import logging
import threading
import time


__author__ = "Wojciech 'KosciaK' Pietrzok"


log = logging.getLogger(__name__)


class EventDispatcher(threading.Thread):

    """Checks the event queue and dispatches events to correct handlers.

    EventDispatcher will run in separate thread. Thread is started 
    after first EventHandler is registered, and stopped when there are no
    handlers left.

    """

    def __init__(self, display):
        threading.Thread.__init__(self, name='EventDispatcher')
        self.setDaemon(True)
        self.__display = display
        self.__root = display.screen().root
        self.__handlers = {} # {event.type: {window.id: set([handler, ]), }, }

    def run(self):
        """Main loop - perform event queue checking.

        Every 100ms check event queue for pending events and dispatch them.
        If there are no registered handlers stop running.

        """
        log.debug('EventDispatcher started')
        while self.__handlers:
            while self.__display.pending_events():
                self.__dispatch(self.__display.next_event())
            time.sleep(0.1)
        log.debug('EventDispatcher stopped')

    def register(self, window, handler):
        """Register event handler and return new window's event mask."""
        log.debug('Registering %s for %s' % (handler, window))
        for event_type in handler.types:
            type_handlers = self.__handlers.setdefault(event_type, {})
            win_handlers = type_handlers.setdefault(window.id, set())
            win_handlers.add(handler)
        if not self.isAlive():
            self.start()
        return self.__get_masks(window.id)

    def unregister(self, window=None, handler=None):
        """Unregister event handler and return new window's event mask.
        
        If window is None all handlers for all windows will be unregistered.
        If handler is None all handlers for this window will be unregistered.
        
        """
        if not window:
            log.debug('Unregistering all handlers for all windows')
            self.__handlers.clear()
            return []
        if not handler:
            log.debug('Unregistering all handlers for %s' % (window))
        else:
            log.debug('Unregistering %s for %s' % (handler, window))
        for event_type, type_handlers in self.__handlers.items():
            if not window.id in type_handlers:
                continue
            if handler:
                type_handlers[window.id].discard(handler)
            else:
                type_handlers.pop(window.id, None)
            if not type_handlers:
                self.__handlers.pop(event_type)
        return self.__get_masks(window.id)

    def __get_masks(self, window_id):
        """Return event type masks for given window."""
        masks = set()
        for type_handlers in self.__handlers.values():
            win_handlers = type_handlers.get(window_id, ())
            for handler in win_handlers:
                masks.update(handler.masks)
        return masks

    def __dispatch(self, event):
        """Dispatch raw X event to correct handler.

        X.KeyPress
            event.window - window the event is reported on
        X.DestroyNotify
            event.window - window that was destroyed
        X.CreateNotify
            event.parent - parent of the new window
            event.window - new window
        X.PropertyNotify
            event.window - window which the property was changed
        X.ConfigureNotify
            event.event - the window the event is generated for
            event.window - the window that has been changed

        """
        if not event.type in self.__handlers:
            # Just skip unwanted events types
            return
        type_handlers = self.__handlers[event.type]
        handlers = []
        if hasattr(event, 'parent') and event.parent.id in type_handlers:
            handlers.extend(type_handlers[event.parent.id])
        elif hasattr(event, 'event') and event.event.id in type_handlers:
            handlers.extend(type_handlers[event.event.id])
        elif hasattr(event, 'window') and event.window.id in type_handlers:
            handlers.extend(type_handlers[event.window.id])
        if self.__root in type_handlers:
            handlers.extend(type_handlers[self.__root])
        for handler in handlers:
            handler.handle_event(event)

