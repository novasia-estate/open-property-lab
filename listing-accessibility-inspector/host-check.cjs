const path=require('node:path');
require('@vscode/test-electron').runTests({extensionDevelopmentPath:__dirname,extensionTestsPath:path.join(__dirname,'host-test.cjs'),launchArgs:['--disable-extensions','--no-sandbox']}).then(()=>console.log('PASS actual VS Code extension host')).catch(e=>{console.error(e);process.exitCode=1;});
