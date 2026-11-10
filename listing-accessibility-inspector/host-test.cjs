exports.run=async()=>{
 const vscode=require('vscode'),assert=require('node:assert/strict');
 const bad=await vscode.workspace.openTextDocument({language:'html',content:'<img src="room.jpg"><a href="/unit"></a><input placeholder="Price">'});
 await vscode.window.showTextDocument(bad);
 await vscode.commands.executeCommand('listingAccessibility.inspect');
 assert.deepEqual(vscode.languages.getDiagnostics(bad.uri).map(d=>d.code).sort(),['empty-action-name','image-alternative','input-label']);
 const good=await vscode.workspace.openTextDocument({language:'html',content:'<button>View floor plan</button>'});
 await vscode.window.showTextDocument(good);await vscode.commands.executeCommand('listingAccessibility.inspect');
 assert.equal(vscode.languages.getDiagnostics(good.uri).length,0);
};
