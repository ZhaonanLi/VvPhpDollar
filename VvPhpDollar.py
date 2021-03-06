'''
VvPhpDollar is a free software under MIT license,
providing a convenient way to insert PHP Dollar Sign.

Compatible with Sublime Text 2 and 3.

Copyright (c) 2015, Zhaonan Li.
All rights reserved.

'''


import os
import sublime
import sublime_plugin


is_ST2 = int(sublime.version()) < 3000


def Singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@Singleton
class VvPhpDollar():

    def __init__(self):

        self.SETTINGS_FILE_NAME = "VvPhpDollar.sublime-settings"
        self.SETTINGS_CALLBACK_KEY = "vv_php_dollar_call_back_key"

        self.vv_settings = None
        self.vv_sign = None
        self.syntax_list = None

        self.__load_settings()

    def __load_settings(self):
        self.vv_settings = sublime.load_settings(self.SETTINGS_FILE_NAME)
        self.__refresh_settings()
        self.vv_settings.add_on_change(self.SETTINGS_CALLBACK_KEY,
                                       self.__refresh_settings)

    def __refresh_settings(self):
        self.vv_sign = self.vv_settings.get("vv_sign", None)
        if not self.vv_sign:
            print ("Please add value of vv_sign into " +\
                   self.SETTINGS_FILE_NAME + " file.")

        self.syntax_list = self.vv_settings.get("syntax_list", [])
        if not self.syntax_list:
            print ("Please add contents of syntax_list into " +\
                   self.SETTINGS_FILE_NAME + " file.")

    def get_syntax_name(self, view):
        syntax = os.path.basename(view.settings().get("syntax"))
        syntax = os.path.splitext(syntax)[0]
        return syntax

    def replace_vv_sign_by_dollar(self, view):
        # Early break
        historyCmd = view.command_history(0)
        if not historyCmd[0] == 'insert' or \
           not historyCmd[1]['characters'] == self.vv_sign[-1]:
            return

        # Fix the issue that breaks functionality for Ctrl+Z
        historyCmd = view.command_history(1)
        if historyCmd[0] == 'vv_php_dollar':
            return

        vv_sign_len = len(self.vv_sign)

        # Locate the last edit regions.
        for last_edit_region in view.sel():
            last_begin = last_edit_region.begin()
            last_end = last_edit_region.end()

            if last_begin - vv_sign_len >= 0:
                # Calculate possible vv region.
                possible_vv_region = sublime.Region(last_begin - vv_sign_len,
                                                    last_end)

                if view.substr(possible_vv_region) == self.vv_sign:
                    view.run_command("vv_php_dollar",
                                     {"begin": possible_vv_region.begin(), "end": possible_vv_region.end()})


class VvPhpDollarCommand(sublime_plugin.TextCommand):

    def run(self, edit, begin, end):
        self.view.replace(edit, sublime.Region(int(begin), int(end)), '$')


class VvPhpDollarListener(sublime_plugin.EventListener):

    def on_modified(self, view):
        vv = VvPhpDollar()
        if vv.get_syntax_name(view) in vv.syntax_list:
            vv.replace_vv_sign_by_dollar(view)


def plugin_loaded():
    VvPhpDollar()


def plugin_unloaded():
    vv = VvPhpDollar()
    vv.vv_settings.clear_on_change(vv.SETTINGS_CALLBACK_KEY)


unload_handler = plugin_unloaded if is_ST2 else lambda: None

if is_ST2:
    plugin_loaded()
