const path = require('path');
const CopyPlugin = require('copy-webpack-plugin');

module.exports = {
    mode: 'development',
    entry: {
        background: path.resolve(__dirname, 'background.js'),
        content: path.resolve(__dirname, 'content.js'),
        settings: path.resolve(__dirname, 'settings.js'),
    },
    resolve: {
        modules: [
            path.resolve(__dirname, '../../..'),
            path.resolve(__dirname, '../../../node_modules'),
        ],
    },
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, 'dist'),
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
                test: /\.(css)$/,
                use: ['style-loader', 'css-loader'],
            },
        ],
    },
    plugins: [
        new CopyPlugin([
            {from: path.resolve(__dirname, 'manifest.json')},
            {from: path.resolve(__dirname, 'settings.html')},
        ]),
    ],
    devtool: 'source-map',
};
