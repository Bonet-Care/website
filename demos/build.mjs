// Bundles the animated demos (React + the Stageshow kit) into js/demos.js and css/demos.css.
import { build } from 'esbuild'
await build({
  entryPoints: ['src/main.tsx'],
  bundle: true, minify: true, format: 'iife', target: ['es2020'],
  outfile: '../js/demos.js', // css lands next to it as demos.css
  loader: { '.svg': 'dataurl', '.png': 'dataurl', '.webp': 'dataurl' },
  define: { 'process.env.NODE_ENV': '"production"' },
  jsx: 'automatic', legalComments: 'none', logLevel: 'info',
})
import { renameSync } from 'node:fs'
renameSync('../js/demos.css', '../css/demos.css')
