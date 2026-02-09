/**
 * Code Explorer - File Tree Component
 * 
 * Renders a hierarchical view of the project's folder structure.
 * Features:
 * - Fetches file structure from the API
 * - Collapsible folders
 * - Clicking a file triggers a callback
 */
class FileTree {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.onFileClick = null; // Callback for file clicks
        this.availableNodes = []; // Store available nodes from graph
    }

    /**
     * Set available nodes from the graph
     * This is used to mark files that are not in the graph
     */
    setAvailableNodes(nodes) {
        this.availableNodes = nodes.map(n => n.id.replace(/\\/g, '/'));
        // Re-render if tree already loaded
        if (this.container.innerHTML) {
            this._updateFileAvailability();
        }
    }

    async load() {
        try {
            const response = await fetch('/api/visualizer/file-structure');
            const fileStructure = await response.json();
            this.render(fileStructure);
        } catch (error) {
            console.error('Failed to load file structure:', error);
            this.container.innerHTML = '<p style="color: #dc3545;">Error loading file tree.</p>';
        }
    }

    render(data) {
        if (!this.container) return;
        this.container.innerHTML = this._buildTreeHTML(data.children, 0);
        this._attachEventListeners();
        this._updateFileAvailability();
    }

    _buildTreeHTML(items, level) {
        let html = `<ul class="file-tree-level-${level}">`;

        items.sort((a, b) => {
            // Sort folders first, then files, then alphabetically
            if (a.type === 'folder' && b.type !== 'folder') return -1;
            if (a.type !== 'folder' && b.type === 'folder') return 1;
            return a.name.localeCompare(b.name);
        });

        for (const item of items) {
            if (item.type === 'folder') {
                html += `
                    <li class="file-tree-item folder">
                        <div class="file-tree-label" data-path="${item.path}">
                            <span class="folder-toggle">▶</span>
                            <span class="folder-icon">📁</span>
                            ${item.name}
                        </div>
                        ${this._buildTreeHTML(item.children, level + 1)}
                    </li>
                `;
            } else {
                html += `
                    <li class="file-tree-item file">
                        <div class="file-tree-label" data-path="${item.path}">
                            <span class="file-icon">📄</span>
                            ${item.name}
                        </div>
                    </li>
                `;
            }
        }

        html += '</ul>';
        return html;
    }

    _attachEventListeners() {
        this.container.querySelectorAll('.file-tree-label').forEach(label => {
            label.addEventListener('click', (event) => {
                const target = event.currentTarget;
                const item = target.parentElement;
                const path = target.dataset.path;

                if (item.classList.contains('folder')) {
                    // Toggle folder visibility
                    item.classList.toggle('open');
                    const toggle = target.querySelector('.folder-toggle');
                    if (toggle) {
                        toggle.textContent = item.classList.contains('open') ? '▼' : '▶';
                    }
                } else {
                    // Handle file click
                    console.log('File clicked in tree:', path);
                    console.log('onFileClick callback exists?', !!this.onFileClick);

                    // Check if file is available in graph
                    if (target.classList.contains('unavailable')) {
                        console.warn('File not available in graph (parse error or filtered out)');
                        return; // Don't proceed if file is unavailable
                    }

                    // Remove active class from all file labels
                    this.container.querySelectorAll('.file-tree-label').forEach(lbl => {
                        lbl.classList.remove('active');
                    });

                    // Add active class to clicked file
                    target.classList.add('active');

                    if (this.onFileClick) {
                        console.log('Calling onFileClick callback with path:', path);
                        this.onFileClick(path);
                    } else {
                        console.warn('onFileClick callback not set!');
                    }
                }
            });
        });
    }

    /**
     * Update file availability based on available nodes from graph
     */
    _updateFileAvailability() {
        if (this.availableNodes.length === 0) return;

        this.container.querySelectorAll('.file-tree-item.file .file-tree-label').forEach(label => {
            const filePath = label.dataset.path.replace(/\\/g, '/');

            // Check if this file exists in the graph using same matching logic as BubbleGraph
            const isAvailable = this.availableNodes.some(nodePath => {
                // Try multiple matching strategies
                if (nodePath === filePath) return true;
                if (nodePath.endsWith(filePath)) return true;
                if (filePath.endsWith(nodePath)) return true;

                // Remove first segment and try again
                const fileParts = filePath.split('/');
                if (fileParts.length > 1) {
                    const fileWithoutFirst = fileParts.slice(1).join('/');
                    if (nodePath === fileWithoutFirst ||
                        nodePath.endsWith(fileWithoutFirst) ||
                        fileWithoutFirst.endsWith(nodePath)) {
                        return true;
                    }
                }

                return false;
            });

            if (!isAvailable) {
                label.classList.add('unavailable');
                label.title = 'File not available in graph (parse error or filtered)';
            } else {
                label.classList.remove('unavailable');
                label.title = '';
            }
        });
    }

    // Add a ready property that resolves when the tree is loaded
    ready() {
        return new Promise((resolve) => {
            if (this.container.innerHTML) {
                resolve();
            } else {
                const observer = new MutationObserver(() => {
                    if (this.container.innerHTML) {
                        observer.disconnect();
                        resolve();
                    }
                });
                observer.observe(this.container, { childList: true });
            }
        });
    }

    /**
     * Highlight a file in the tree by its path
     * @param {string} filepath - The path of the file to highlight
     */
    highlightFile(filepath) {
        // Remove active class from all file labels
        this.container.querySelectorAll('.file-tree-label').forEach(lbl => {
            lbl.classList.remove('active');
        });

        // Find and highlight the matching file
        const normalizedSearchPath = filepath.replace(/\\/g, '/');
        const labels = this.container.querySelectorAll('.file-tree-label');

        for (const label of labels) {
            const labelPath = label.dataset.path.replace(/\\/g, '/');
            if (labelPath === normalizedSearchPath || labelPath.endsWith(normalizedSearchPath)) {
                label.classList.add('active');

                // Expand parent folders to make it visible
                let parent = label.parentElement;
                while (parent && parent !== this.container) {
                    if (parent.classList.contains('folder')) {
                        parent.classList.add('open');
                        const toggle = parent.querySelector('.folder-toggle');
                        if (toggle) {
                            toggle.textContent = '▼';
                        }
                    }
                    parent = parent.parentElement;
                }

                // Scroll into view
                label.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                break;
            }
        }
    }
}