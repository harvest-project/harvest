const path = require('path');
const fs = require('fs');

const pluginsRoot = path.resolve(__dirname, 'plugins');

function discoverPlugins() {
    const pluginDirs = fs.readdirSync(pluginsRoot);
    const plugins = [];
    for (const pluginName of pluginDirs) {
        const pluginDir = path.resolve(pluginsRoot, pluginName);
        if (pluginName.startsWith('_') || pluginName.startsWith('.')) {
            continue;
        }
        const indexJsPath = path.resolve(pluginDir, 'assets', 'index.js');
        if (!fs.existsSync(indexJsPath)) {
            continue;
        }
        plugins.push({
            name: pluginName,
            path: pluginDir,
            entryPath: indexJsPath,
        });
    }
    return plugins;
}

const plugins = discoverPlugins();
const entries = plugins.map(plugin => plugin.entryPath).concat([
    './home/assets/index.js',
]);

module.exports = {
    mode: 'development',
    entry: entries,
    resolve: {
        modules: [
            __dirname,
            'node_modules',
        ],
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            ['@babel/preset-env', {
                                'targets':
                                    'last 2 Edge major versions,' +
                                    'last 2 Chrome major versions,' +
                                    'last 2 Firefox versions,' +
                                    'Firefox ESR,' +
                                    'last 2 Opera versions,' +
                                    'last 2 ChromeAndroid versions,' +
                                    'last 2 FirefoxAndroid versions,' +
                                    'last 2 iOS versions,' +
                                    'last 2 Safari major versions',
                            }],
                            ['@babel/preset-react', {}],
                        ],
                        plugins: [
                            ['@babel/plugin-proposal-decorators', {legacy: true}],
                            ['@babel/plugin-proposal-class-properties', {loose: true}],
                        ],
                    },
                },
            },
            {
                test: /\.(png|jpg|gif)$/i,
                use: [
                    {
                        loader: 'url-loader',
                        options: {
                            limit: 2048,
                            publicPath: '/static',
                        },
                    },
                ],
            },
            {
                test: /\.(css)$/i,
                use: ['style-loader', 'css-loader'],
            },
            {
                test: /\.(less)$/i,
                use: [
                    {loader: 'style-loader'},
                    {
                        loader: 'css-loader',
                        options: {
                            sourceMap: true,
                            modules: true,
                            localIdentName: '[local]___[hash:base64:5]',
                        },
                    },
                    {
                        loader: 'less-loader',
                        options: {
                            javascriptEnabled: true,
                        },
                    },
                ],
            },
        ],
    },
    output: {
        filename: 'app.js',
        path: path.resolve(__dirname, 'dist'),
    },
    devtool: 'eval-source-map',
    optimization: {
        usedExports: true,
    },
};
