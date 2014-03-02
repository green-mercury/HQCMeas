# -*- coding: utf-8 -*-
#==============================================================================
# module : pref_plugin.py
# author : Matthieu Dartiailh
# license : MIT license
#==============================================================================
import os
from atom.api import Str, Unicode, Typed, Dict
from enaml.workbench.api import Plugin
from configobj import ConfigObj

from .preferences import Preferences


MODULE_PATH = os.path.dirname(__file__)

PREFS_POINT = 'hqc_meas.preferences.pref_plugins'


class PrefPlugin(Plugin):
    """

    """
    # Folder in which the default file is located
    default_folder = Unicode()

    # Name of the default file
    default_file = Unicode()

    def start(self):
        """ Start the plugin life-cycle.

        This method is called by the framework at the appropriate time. It
        should never be called by user code.

        """
        self._pref_decls = {}
        def_path = os.path.join(MODULE_PATH, 'default.ini')
        if os.path.isfile(def_path):
            defaults = ConfigObj(def_path)
            self.default_folder = defaults['folder']
            self.default_file = defaults['file']
            pref_path = os.path.join(defaults['folder'], defaults['file'])
            if os.path.isfile(pref_path):
                self._prefs = ConfigObj(pref_path).dict()

        self._bind_observers()

    def stop(self):
        """ Stop the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        self._unbind_observers()
        self._pref_decls.clear()
        pref_path = os.path.join(self.default_folder, self.default_file)
        if os.path.isfile(pref_path):
            prefs = ConfigObj()
            prefs.update(self._prefs)
            prefs.filename = pref_path
            prefs.write()

        def_path = os.path.join(MODULE_PATH, 'default.ini')
        if not os.path.isfile(def_path):
            defaults = ConfigObj(def_path)
            defaults['folder'] = self.default_folder
            defaults['file'] = self.default_file

    def save_preferences(self, path=None):
        """ Collect and save preferences for all registered plugins.

        Parameters
        ----------
        path : str, optional
            Path of the file in which save the preferences. In its absence
            the default file is used.

        """
        if path is None:
            path = os.path.join(self.default_folder, self.default_file)

        prefs = ConfigObj(path)
        for plugin_id in self._pref_decls:
            plugin = self.workbench.get_plugin(plugin_id)
            decl = self._pref_decls[plugin_id]
            save_method = getattr(plugin, decl.load_method)
            prefs[plugin_id] = save_method()

        prefs.write()

    def load_preferences(self, path=None):
        """ Load preferences and update all registered plugin.

        Parameters
        ----------
        path : str, optional
            Path to the file storing the preferences. In its absence default
            preferences are loaded.

        """
        if path is None:
            path = os.path.join(self.default_folder, self.default_file)

        prefs = ConfigObj(path)
        for plugin_id in prefs:
            if plugin_id in self._pref_decls:
                plugin = self.workbench.get_plugin(plugin_id)
                decl = self._pref_decls[plugin_id]
                load_method = getattr(plugin, decl.load_method)
                load_method(prefs[plugin_id])

    def plugin_init_complete(self, plugin_id):
        """ Notify the preference plugin that a plugin has started properly.

        This method should be called by a plugin once it has started and loaded
        its preferences. This call is necessary to avoid overriding values for
        for auto-save members by default values.

        Parameters
        ----------
        plugin_id : str
            Id of the plugin which has started.

        """
        plugin = self.workbench.get_plugin(plugin_id)
        pref_decl = self._pref_decls[plugin_id]
        for member in pref_decl.auto_save:
            # Custom observer which does not rely on the fact that the object
            # in the change dictionnary is a plugin
            # TODO add support for dotted names
            observer = lambda x: self._auto_save_update(plugin_id, x)
            plugin.observe(member, observer)

    def plugin_preferences(self, plugin_id):
        """ Access to the preferences values stored for a plugin.

        Parameters
        ----------
        plugin_id : str
            Id of the plugin whose preferences values should be returned.

        Returns
        -------
        prefs : dict(str, str)
            Preferences for the plugin as a dict.

        """
        if self._prefs:
            return self._prefs.get(plugin_id, {})
        else:
            return {}

    def update_plugin_preferences(self, plugin_id):
        """ Update the preferences using the current value of a plugin.

        Parameters
        ----------
        plugin_id : str
            Id of the plugin for which the values of the preferences, should
            be updated

        """
        decl = self._pref_decls[plugin_id]
        plugin = self.workbench.get_plugin(plugin_id)
        save_method = getattr(plugin, decl.save_method)
        self._prefs[plugin_id] = save_method()

    def open_editor(self):
        """
        """
        # TODO here must build all editors from declaration, open dialog
        # and manage the update if the user validate.

    #---- Private API ---------------------------------------------------------

    # ConfigObj object in which the preferences are stored as strings
    _prefs = Typed(ConfigObj)

    # Mapping between plugin_id and the declared preferences.
    _pref_decls = Dict(Str(), Typed(Preferences))

    def _refresh_pref_decl(self):
        """ Refresh the list of states contributed by extensions.

        """
        workbench = self.workbench
        point = workbench.get_extension_point(PREFS_POINT)
        extensions = point.extensions

        # If no extension remain clear everything
        if not extensions:
            self._pref_decls.clear()
            return

        # Map extension to preference declaration
        new_ids = dict()
        old_ids = self._pref_decls
        for extension in extensions:
            if extension.plugin_id in old_ids:
                pref = old_ids[extension.plugin_id]
            else:
                pref = self._load_pref_decl(extension)
            new_ids[extension] = pref

        self._pref_decls = new_ids

    def _load_pref_decl(self, extension):
        """ Get the Preferences contributed by an extension

        Parameters
        ----------
        extension : Extension
            Extension contributing to the pref extension point.

        Returns
        -------
        pref_decl : Preferences
            Preference object contributed by the extension.
        """
        # Getting the pref declaration contributed by the extension, either
        # as a child or returned by the factory. Only the first state is
        # considered.
        workbench = self.workbench
        prefs = extension.get_children(Preferences)
        if extension.factory is not None and not prefs:
            pref = extension.factory(workbench)
            if not isinstance(pref, Preferences):
                msg = "extension '%s' created non-Preferences of type '%s'"
                args = (extension.qualified_id, type(pref).__name__)
                raise TypeError(msg % args)
        else:
            pref = prefs[0]

        return pref

    def _auto_save_update(self, plugin_id, change):
        """ Observer for the auto-save members

        Parameters
        ----------
        plugin_id : str
            Id of the plugin owner of the member being observed

        change : dict
            Change dictionnary given by Atom

        """
        name = change['name']
        value = change['value']
        if plugin_id in self._prefs:
            self._prefs[plugin_id][name] = value
        else:
            self._prefs[plugin_id] = {name: value}

    def _on_pref_decls_updated(self, change):
        """ The observer for the state extension point

        """
        self._refresh_pref_decls()

    def _bind_observers(self):
        """ Setup the observers for the plugin.

        """
        workbench = self.workbench
        point = workbench.get_extension_point(PREFS_POINT)
        point.observe('extensions', self._on_pref_decls_updated)

    def _unbind_observers(self):
        """ Remove the observers for the plugin.

        """
        workbench = self.workbench
        point = workbench.get_extension_point(PREFS_POINT)
        point.unobserve('extensions', self._on_pref_decls_updated)
