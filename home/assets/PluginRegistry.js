export const plugins = [];

export function registerPlugin(plugin) {
    if (plugins.indexOf(plugin) === -1) {
        plugins.push(plugin);
    }
}
