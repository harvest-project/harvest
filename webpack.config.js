const path = require('path');
const fs = require('fs');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const pluginsRoot = path.resolve(__dirname, 'plugins');

class PluginInfo {
    constructor(name) {
        this.name = name;
        this.path = path.resolve(pluginsRoot, this.name);
        this.assetsEntryPath = path.resolve(this.path, 'assets', 'index.js');
        this.hasAssets = fs.existsSync(this.assetsEntryPath);
        this.extensionWebpackConfigPath = path.resolve(this.path, 'extension', 'webpack.local.js');
        this.hasExtension = fs.existsSync(this.extensionWebpackConfigPath);
    }
}

function discoverPlugins() {
    const pluginDirs = fs.readdirSync(pluginsRoot);
    const plugins = [];
    for (const pluginName of pluginDirs) {
        if (pluginName.startsWith('_') || pluginName.startsWith('.')) {
            continue;
        }
        plugins.push(new PluginInfo(pluginName));
    }
    return plugins;
}

const plugins = discoverPlugins();
const entries = plugins.filter(p => p.hasAssets).map(p => p.assetsEntryPath).concat([
    './home/assets/index.js',
]);
const pluginExtensionConfigs = plugins.filter(p => p.hasExtension)
    .map(p => require(p.extensionWebpackConfigPath));

module.exports = [{
    mode: 'development',
    entry: entries,
    resolve: {
        modules: [
            __dirname,
            'node_modules',
        ],
    },
    output: {
        filename: 'main.js',
        path: path.resolve(__dirname, 'dist'),
        publicPath: '/static/',
    },
    optimization: {
        usedExports: true,
    },
    plugins: [
        new MiniCssExtractPlugin(),
    ],
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
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                ],
            },
            {
                test: /\.(less)$/i,
                use: [
                    MiniCssExtractPlugin.loader,
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
    devtool: 'eval-source-map',
    devServer: {
        index: '',
        port: 9092,
        proxy: {
            '!/static/**/*': 'http://localhost:9090',
        },
    },
}].concat(pluginExtensionConfigs);
