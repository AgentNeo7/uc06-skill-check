import { analyze } from './index.mjs';
import { cli } from './common.mjs';
try { cli(analyze); } catch(e) { console.error(JSON.stringify({status:'error',message:e.message}));process.exitCode=2; }
