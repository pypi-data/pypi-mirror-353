import { JupyterFrontEnd } from '@jupyterlab/application';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';

/**
 * Interface for session data that will be displayed in the popup
 */
export interface SessionData {
  timestamp: string;
  notebookPath?: string;
  kernelId?: string;
  kernelName?: string;
  kernelState?: string;
  sessionName?: string;
  userId?: string;
  jupyterlabVersion?: string;
  currentWidget?: string;
}

/**
 * SessionTracer class that monitors JupyterLab sessions and collects current session information
 */
export class SessionTracer {
  private app: JupyterFrontEnd;
  private docManager: IDocumentManager;
  private notebookTracker: INotebookTracker;

  constructor(
    app: JupyterFrontEnd,
    docManager: IDocumentManager,
    notebookTracker: INotebookTracker
  ) {
    this.app = app;
    this.docManager = docManager;
    this.notebookTracker = notebookTracker;
  }

  /**
   * Start the session tracer
   */
  start(): void {
    console.log('Starting Session Tracer...');
    this.setupNotebookTracking();
  }

  /**
   * Setup tracking for notebook-specific events
   */
  private setupNotebookTracking(): void {
    // Track when notebooks are added to the tracker
    this.notebookTracker.widgetAdded.connect((sender: any, notebook: NotebookPanel) => {
      console.log('Notebook opened:', notebook.context.path);
      
      // Track when the notebook's kernel changes
      notebook.context.sessionContext.kernelChanged.connect((context: any, args: any) => {
        console.log('Kernel changed for notebook:', notebook.context.path, {
          oldKernelId: args.oldValue?.id,
          newKernelId: args.newValue?.id,
          kernelName: args.newValue?.name
        });
      });

      // Track notebook saves
      notebook.context.fileChanged.connect(() => {
        console.log('Notebook saved:', notebook.context.path);
      });
    });

    // Track current notebook changes
    this.notebookTracker.currentChanged.connect((sender: any, notebook: NotebookPanel | null) => {
      if (notebook) {
        console.log('Notebook activated:', notebook.context.path);
      }
    });
  }

  /**
   * Get comprehensive current session information
   */
  getCurrentSessionInfo(): SessionData {
    const currentNotebook = this.notebookTracker.currentWidget;
    const sessionData: SessionData = {
      timestamp: new Date().toISOString(),
      jupyterlabVersion: this.app.version,
      currentWidget: currentNotebook?.title.label
    };

    // Get current active notebook info
    if (currentNotebook) {
      // Get server URL and combine with notebook path
      const serverUrl = this.app.serviceManager.serverSettings.baseUrl;
      const notebookPath = currentNotebook.context.path;
      sessionData.notebookPath = `${serverUrl}${notebookPath}`;
      
      sessionData.sessionName = currentNotebook.context.sessionContext.session?.name;
      
      const kernel = currentNotebook.context.sessionContext.session?.kernel;
      if (kernel) {
        sessionData.kernelId = kernel.id;
        sessionData.kernelName = kernel.name;
        sessionData.kernelState = kernel.connectionStatus;
      }
    }

    return sessionData;
  }

  /**
   * Get formatted JSON string for display
   */
  getFormattedSessionInfo(): string {
    const sessionData = this.getCurrentSessionInfo();
    return JSON.stringify(sessionData, null, 2);
  }

  /**
   * Stop the session tracer
   */
  stop(): void {
    console.log('Session Tracer stopped');
  }
} 
