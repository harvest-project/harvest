export const plugins = [];
export const pluginsByName = {};

export function registerPlugin(plugin) {
    if (pluginsByName.hasOwnProperty(plugin.pluginName)) {
        throw `Plugin ${plugin.pluginName} already registered.`;
    }
    pluginsByName[plugin.pluginName] = plugin;
    if (plugins.indexOf(plugin) === -1) {
        plugins.push(plugin);
    }
}
