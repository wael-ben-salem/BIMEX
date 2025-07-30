import {nodeResolve} from '@rollup/plugin-node-resolve';
import css from "rollup-plugin-import-css";
import url from "@rollup/plugin-url";

export default {
    input: './index.js',
    output: [{
        file: './dist/xeokit-bim-viewer.es.js',
        format: 'es',
        name: 'bundle'
    },],
    plugins: [
        css(),
        nodeResolve({
            // 🔧 CORRECTION: Résoudre les modules externes comme FontAwesome
            preferBuiltins: false,
            browser: true
        }),
        url({
            include: ['**/*.woff', '**/*.woff2', '**/*.ttf', '**/*.eot', '**/*.svg'],
            limit: 1024 * 1024, // 1MB limit pour inclure les polices dans le bundle
            // 🔧 CORRECTION: Générer des URLs relatives pour les polices
            fileName: 'fonts/[name][extname]',
            publicPath: './fonts/'
        }),
    ],
    // 🔧 CORRECTION: Marquer FontAwesome comme externe pour éviter les erreurs de résolution
    external: [
        '@fortawesome/fontawesome-free/webfonts/fa-regular-400.woff2',
        '@fortawesome/fontawesome-free/webfonts/fa-solid-900.woff2',
        '@fortawesome/fontawesome-free/webfonts/fa-regular-400.ttf',
        '@fortawesome/fontawesome-free/webfonts/fa-brands-400.ttf',
        '@fortawesome/fontawesome-free/webfonts/fa-brands-400.woff2',
        '@fortawesome/fontawesome-free/webfonts/fa-solid-900.ttf'
    ]
}