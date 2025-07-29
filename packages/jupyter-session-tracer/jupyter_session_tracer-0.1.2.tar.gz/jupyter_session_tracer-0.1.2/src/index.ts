import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { IDocumentManager } from '@jupyterlab/docmanager';

import { INotebookTracker } from '@jupyterlab/notebook';

import { IMainMenu } from '@jupyterlab/mainmenu';

import { ICommandPalette } from '@jupyterlab/apputils';

import { MainAreaWidget } from '@jupyterlab/apputils';

import { Menu } from '@lumino/widgets';

import { SessionTracer } from './sessionTracer';
import { SessionPopup } from './sessionPopup';

/**
 * The command IDs used by the session tracer plugin.
 */
namespace CommandIDs {
  export const showSessionInfo = 'session-tracer:show-info';
}

/**
 * Initialization data for the jupyter-session-tracer extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyter-session-tracer:plugin',
  description: 'A JupyterLab extension that shows session information in a popup',
  autoStart: true,
  requires: [IDocumentManager, INotebookTracker],
  optional: [IMainMenu, ICommandPalette],
  activate: (
    app: JupyterFrontEnd,
    docManager: IDocumentManager,
    notebookTracker: INotebookTracker,
    mainMenu: IMainMenu | null,
    palette: ICommandPalette | null
  ) => {
    console.log('JupyterLab extension jupyter-session-tracer is activated!');

    // Initialize the session tracer
    const sessionTracer = new SessionTracer(app, docManager, notebookTracker);
    sessionTracer.start();

    // Add command to show session info
    const command = CommandIDs.showSessionInfo;
    app.commands.addCommand(command, {
      label: '📊 Show Session Info',
      caption: 'Display current JupyterLab session information',
      execute: () => {
        // Get current session information
        const sessionData = sessionTracer.getCurrentSessionInfo();
        
        // Create the popup widget
        const popup = new SessionPopup(sessionData);
        
        // Create a main area widget to hold the popup
        const widget = new MainAreaWidget({ content: popup });
        widget.id = 'session-info-popup';
        widget.title.label = '📊 Session Information';
        widget.title.closable = true;
        
        // Add the widget to the main area
        if (!widget.isAttached) {
          app.shell.add(widget, 'main');
        }
        
        // Activate the widget
        app.shell.activateById(widget.id);
      }
    });

    // Add command to main menu if available - place next to Help menu
    if (mainMenu) {
      // Create a new menu for session info
      const sessionInfoMenu = new Menu({ commands: app.commands });
      sessionInfoMenu.title.label = '📊 Session Info';
      sessionInfoMenu.addItem({ command });
      
      // Add the menu to the main menu bar
      mainMenu.addMenu(sessionInfoMenu);
    }

    // Add command to command palette if available
    if (palette) {
      palette.addItem({
        command,
        category: 'Session Tracer'
      });
    }

    // Add toolbar button to the top area
    const toolbarButton = document.createElement('button');
    toolbarButton.className = 'jp-ToolbarButton jp-SessionTracer-toolbarButton';
    toolbarButton.title = 'Show Session Information';
    toolbarButton.innerHTML = '📊';
    toolbarButton.onclick = () => {
      app.commands.execute(command);
    };

    // Add some styling to the button
    toolbarButton.style.cssText = `
      background: none;
      border: none;
      font-size: 16px;
      padding: 4px 8px;
      cursor: pointer;
      border-radius: 4px;
      margin: 0 4px;
      transition: background-color 0.2s;
    `;

    // Add hover effect
    toolbarButton.addEventListener('mouseenter', () => {
      toolbarButton.style.backgroundColor = 'var(--jp-layout-color2)';
    });
    
    toolbarButton.addEventListener('mouseleave', () => {
      toolbarButton.style.backgroundColor = 'transparent';
    });

    // Try to add the button to the top bar
    const addButtonToTopBar = () => {
      const topBar = document.querySelector('.jp-MenuBar');
      if (topBar) {
        topBar.appendChild(toolbarButton);
        return true;
      }
      return false;
    };

    // Try immediately, then retry after a delay if needed
    if (!addButtonToTopBar()) {
      setTimeout(() => {
        addButtonToTopBar();
      }, 1000);
    }

    console.log('Session tracer toolbar button added');
  }
};

export default plugin; 