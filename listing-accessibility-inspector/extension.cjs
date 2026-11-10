'use strict';
const vscode=require('vscode');const {inspect}=require('./inspect.cjs');
function activate(context){
 const collection=vscode.languages.createDiagnosticCollection('listing-accessibility');context.subscriptions.push(collection);
 const versions=new Map();
 async function review(doc){
  if(doc.languageId!=='html')return;
  if(!vscode.workspace.getConfiguration('listingAccessibility').get('enabled',true)){collection.delete(doc.uri);return;}
  const key=doc.uri.toString(),version=doc.version;versions.set(key,version);
  try{
   const issues=await inspect(doc.getText());
   if(versions.get(key)!==version||doc.isClosed)return;
   collection.set(doc.uri,issues.map(x=>{const d=new vscode.Diagnostic(new vscode.Range(doc.positionAt(x.start),doc.positionAt(x.end)),x.message,vscode.DiagnosticSeverity.Warning);d.source='Listing Accessibility';d.code=x.rule;return d;}));
  }catch(e){collection.delete(doc.uri);vscode.window.setStatusBarMessage(`Listing Accessibility: ${e.message}`,6000);}
 }
 context.subscriptions.push(vscode.commands.registerCommand('listingAccessibility.inspect',()=>{const e=vscode.window.activeTextEditor;if(e)return review(e.document);}),vscode.workspace.onDidOpenTextDocument(review),vscode.workspace.onDidChangeTextDocument(e=>review(e.document)),vscode.workspace.onDidCloseTextDocument(doc=>{versions.delete(doc.uri.toString());collection.delete(doc.uri);}),vscode.workspace.onDidChangeConfiguration(e=>{if(e.affectsConfiguration('listingAccessibility'))for(const d of vscode.workspace.textDocuments)review(d);}));
 for(const doc of vscode.workspace.textDocuments)review(doc);
}
module.exports={activate,deactivate(){}};
