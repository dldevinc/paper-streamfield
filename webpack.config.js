const path = require("path");
const webpack = require("webpack");
const pixrem = require("pixrem");
const autoprefixer = require("autoprefixer");
const TerserPlugin = require("terser-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");

const SOURCE_DIR = "streamfield/static/streamfield/src";
const DIST_DIR = "streamfield/static/streamfield/dist";

let config = {
    entry: {
        widget: path.resolve(SOURCE_DIR, "widget.js")
    },
    output: {
        clean: true,
        path: path.resolve(DIST_DIR),
        publicPath: "/static/streamfield/dist/",
        filename: "[name].js",
        assetModuleFilename: "assets/[name][ext][query]"
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /[\\/]node_modules[\\/]/,
                use: [
                    {
                        loader: "babel-loader",
                        options: {
                            cacheDirectory: path.resolve(__dirname, "cache")
                        }
                    }
                ]
            },

            {
                test: /\.css$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader
                    },
                    {
                        loader: "fast-css-loader"
                    }
                ]
            },

            {
                test: /\.scss$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader
                    },
                    {
                        loader: "fast-css-loader",
                        options: {
                            importLoaders: 2
                        }
                    },
                    {
                        loader: "postcss-loader",
                        options: {
                            postcssOptions: {
                                plugins: [pixrem(), autoprefixer()]
                            }
                        }
                    },
                    {
                        loader: "sass-loader",
                        options: {
                            sassOptions: {
                                includePaths: [path.resolve(__dirname, "node_modules")]
                            }
                        }
                    }
                ]
            },

            {
                test: /\.(jpe?g|png|gif|woff2?|ttf|eot|svg)$/i,
                type: "asset/resource"
            },

            // https://webpack.js.org/guides/asset-modules/#replacing-inline-loader-syntax
            {
                resourceQuery: /raw/,
                type: "asset/source"
            }
        ]
    },
    resolve: {
        modules: [SOURCE_DIR, "node_modules"]
    },
    plugins: [
        new webpack.ProgressPlugin(),
        new MiniCssExtractPlugin({
            filename: "[name].css"
        })
    ],
    optimization: {
        moduleIds: "deterministic"
    },
    watchOptions: {
        aggregateTimeout: 2000,
        ignored: ["**/node_modules"]
    },
    stats: {
        assets: false,
        chunks: true
    }
};

module.exports = (env, argv) => {
    config.mode = argv.mode === "production" ? "production" : "development";

    if (config.mode === "production") {
        config.devtool = "source-map";
    } else {
        config.devtool = "eval";
    }

    if (config.mode === "development") {
        config.cache = {
            type: "filesystem",
            cacheDirectory: path.resolve(__dirname, "cache"),
            buildDependencies: {
                config: [__filename]
            }
        };
    }

    if (config.mode === "production") {
        config.optimization.minimizer = [
            new TerserPlugin({
                parallel: true
            }),
            new CssMinimizerPlugin({})
        ];
    }

    return config;
};
