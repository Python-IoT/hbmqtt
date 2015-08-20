# Copyright (c) 2015 Nicolas JOUANIN
#
# See the file license.txt for copying permission.
import unittest
import logging
import asyncio
from hbmqtt.plugins.manager import PluginManager, BaseContext

formatter = "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=formatter)


class TestPlugin:
    def __init__(self, context):
        self.context = context


class EventTestPlugin:
    def __init__(self, context):
        self.context = context
        self.test_flag = False
        self.coro_flag = False

    @asyncio.coroutine
    def on_test(self):
        self.test_flag = True
        self.context.logger.info("on_test")

    @asyncio.coroutine
    def test_coro(self):
        self.coro_flag = True


class TestPluginManager(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()

    def test_load_plugin(self):
        manager = PluginManager("hbmqtt.test.plugins", context=None)
        self.assertTrue(len(manager._plugins) > 0)

    def test_fire_event(self):
        @asyncio.coroutine
        def fire_event():
            yield from manager.fire_event("test")
            yield from asyncio.sleep(1, loop=self.loop)
            yield from manager.close()

        manager = PluginManager("hbmqtt.test.plugins", context=None, loop=self.loop)
        self.loop.run_until_complete(fire_event())
        plugin = manager.get_plugin("event_plugin")
        self.assertTrue(plugin.object.test_flag)

    def test_fire_event_wait(self):
        @asyncio.coroutine
        def fire_event():
            yield from manager.fire_event("test", wait=True)
            yield from manager.close()

        manager = PluginManager("hbmqtt.test.plugins", context=None, loop=self.loop)
        self.loop.run_until_complete(fire_event())
        plugin = manager.get_plugin("event_plugin")
        self.assertTrue(plugin.object.test_flag)

    def test_map_coro(self):
        @asyncio.coroutine
        def call_coro():
            yield from manager.map_plugin_coro('test_coro')

        manager = PluginManager("hbmqtt.test.plugins", context=None, loop=self.loop)
        self.loop.run_until_complete(call_coro())
        plugin = manager.get_plugin("event_plugin")
        self.assertTrue(plugin.object.test_coro)
