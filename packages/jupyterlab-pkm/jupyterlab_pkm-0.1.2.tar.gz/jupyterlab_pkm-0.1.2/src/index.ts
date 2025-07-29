import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette } from '@jupyterlab/apputils';
import { IEditorTracker } from '@jupyterlab/fileeditor';
import { IMarkdownViewerTracker } from '@jupyterlab/markdownviewer';
import { INotebookTracker } from '@jupyterlab/notebook';

// Adding plugins back one by one
import { markdownPreviewPlugin } from './markdown-preview';
import { wikilinkPlugin } from './wikilinks';
import { searchPlugin } from './search';
import { backlinksPlugin } from './backlinks';
import { blockEmbeddingPlugin } from './block-embedding';
import { notebookEmbedPlugin } from './notebook-embed';
import { codeCopyPlugin } from './code-copy';
import { welcomePlugin } from './welcome'; // Still causes issues


/**
 * The main extension that combines all PKM features
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab/pkm-extension:plugin',
  description: 'Personal Knowledge Management extension for JupyterLab Desktop',
  autoStart: true,
  requires: [ICommandPalette, IEditorTracker, IMarkdownViewerTracker, INotebookTracker],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    editorTracker: IEditorTracker,
    markdownTracker: IMarkdownViewerTracker,
    notebookTracker: INotebookTracker
  ) => {
    console.log('🎉 JupyterLab PKM extension activated');
    
    // Add a test command to verify it's working
    const testCommand = 'pkm:test-full';
    app.commands.addCommand(testCommand, {
      label: 'PKM: Test Full Extension',
      execute: () => {
        console.log('Full PKM Extension is working!');
        alert('Full PKM Extension loaded successfully!');
      }
    });

    palette.addItem({
      command: testCommand,
      category: 'PKM'
    });
  }
};


/**
 * Export all plugins
 */
export default [
  extension,
  welcomePlugin,
  markdownPreviewPlugin,
  wikilinkPlugin,
  searchPlugin,
  backlinksPlugin,
  blockEmbeddingPlugin,
  notebookEmbedPlugin,
  codeCopyPlugin
];