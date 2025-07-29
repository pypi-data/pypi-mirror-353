import { Widget } from '@lumino/widgets';
import { SessionData } from './sessionTracer';

/**
 * A widget that displays session information in a popup
 */
export class SessionPopup extends Widget {
  private sessionData: SessionData;
  
  constructor(sessionData: SessionData) {
    super();
    this.sessionData = sessionData;
    this.addClass('jp-SessionPopup');
    this.title.label = 'Session Information';
    this.title.closable = true;
    this.createContent();
  }

  /**
   * Create the popup content
   */
  private createContent(): void {
    const container = document.createElement('div');
    container.className = 'jp-SessionPopup-container';
    
    // Header
    const header = document.createElement('div');
    header.className = 'jp-SessionPopup-header';
    header.innerHTML = `
      <h2>📊 Session Information</h2>
      <p>Current JupyterLab session details</p>
    `;
    
    // Copy button
    const copyButton = document.createElement('button');
    copyButton.className = 'jp-SessionPopup-copyButton';
    copyButton.innerHTML = '📋 Copy to Clipboard';
    copyButton.onclick = () => this.copyToClipboard();
    
    // JSON display area
    const jsonContainer = document.createElement('div');
    jsonContainer.className = 'jp-SessionPopup-json';
    
    const preElement = document.createElement('pre');
    preElement.className = 'jp-SessionPopup-jsonContent';
    
    const codeElement = document.createElement('code');
    codeElement.className = 'language-json';
    codeElement.textContent = JSON.stringify(this.sessionData, null, 2);
    
    preElement.appendChild(codeElement);
    jsonContainer.appendChild(preElement);
    
    // Summary info
    const summary = document.createElement('div');
    summary.className = 'jp-SessionPopup-summary';
    summary.innerHTML = this.createSummaryHTML();
    
    // Assemble the popup
    container.appendChild(header);
    container.appendChild(summary);
    container.appendChild(copyButton);
    container.appendChild(jsonContainer);
    
    this.node.appendChild(container);
    
    // Auto-copy to clipboard when popup is shown
    this.copyToClipboard();
    
    // Apply syntax highlighting
    this.applySyntaxHighlighting(codeElement);
  }

  /**
   * Create summary HTML
   */
  private createSummaryHTML(): string {
    const data = this.sessionData;
    return `
      <div class="jp-SessionPopup-summaryGrid">
        <div class="jp-SessionPopup-summaryItem">
          <strong>📓 Current Notebook:</strong> 
          <span>${data.notebookPath || 'None'}</span>
        </div>
        <div class="jp-SessionPopup-summaryItem">
          <strong>🧠 Kernel:</strong> 
          <span>${data.kernelName || 'None'} (${data.kernelState || 'Unknown'})</span>
        </div>
        <div class="jp-SessionPopup-summaryItem">
          <strong>⏰ Timestamp:</strong> 
          <span>${new Date(data.timestamp).toLocaleString()}</span>
        </div>
        <div class="jp-SessionPopup-summaryItem">
          <strong>🔧 JupyterLab Version:</strong> 
          <span>${data.jupyterlabVersion || 'Unknown'}</span>
        </div>
      </div>
    `;
  }

  /**
   * Apply basic syntax highlighting to JSON
   */
  private applySyntaxHighlighting(element: HTMLElement): void {
    const jsonText = element.textContent || '';
    const highlighted = jsonText
      .replace(/"([^"]+)":/g, '<span class="json-key">"$1"</span>:')
      .replace(/:\s*"([^"]*)"/g, ': <span class="json-string">"$1"</span>')
      .replace(/:\s*(\d+)/g, ': <span class="json-number">$1</span>')
      .replace(/:\s*(true|false)/g, ': <span class="json-boolean">$1</span>')
      .replace(/:\s*null/g, ': <span class="json-null">null</span>');
    
    element.innerHTML = highlighted;
  }

  /**
   * Copy session data to clipboard
   */
  private async copyToClipboard(): Promise<void> {
    try {
      const jsonString = JSON.stringify(this.sessionData, null, 2);
      await navigator.clipboard.writeText(jsonString);
      
      // Show feedback
      this.showCopyFeedback();
      console.log('Session data copied to clipboard');
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      
      // Fallback: select all text
      this.selectAllText();
    }
  }

  /**
   * Show visual feedback that content was copied
   */
  private showCopyFeedback(): void {
    const copyButton = this.node.querySelector('.jp-SessionPopup-copyButton') as HTMLButtonElement;
    if (copyButton) {
      const originalText = copyButton.innerHTML;
      copyButton.innerHTML = '✅ Copied!';
      copyButton.style.backgroundColor = '#4CAF50';
      
      setTimeout(() => {
        copyButton.innerHTML = originalText;
        copyButton.style.backgroundColor = '';
      }, 2000);
    }
  }

  /**
   * Fallback method to select all text if clipboard API fails
   */
  private selectAllText(): void {
    const jsonElement = this.node.querySelector('.jp-SessionPopup-jsonContent');
    if (jsonElement) {
      const range = document.createRange();
      range.selectNodeContents(jsonElement);
      const selection = window.getSelection();
      if (selection) {
        selection.removeAllRanges();
        selection.addRange(range);
      }
    }
  }

  /**
   * Update the popup with new session data
   */
  updateSessionData(sessionData: SessionData): void {
    this.sessionData = sessionData;
    this.node.innerHTML = '';
    this.createContent();
  }
} 