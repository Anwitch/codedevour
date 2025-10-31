/**
 * Details Sidebar - File & Function Details Panel
 * 
 * Displays detailed information about selected files and functions:
 * - File statistics (lines, size, functions)
 * - Function list
 * - Import relationships
 * - Imported by (reverse dependencies)
 */

class DetailsSidebar {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.currentFile = null;

        // Callbacks
        this.onFunctionClick = null;
        this.onImportClick = null;

        this._initialize();
    }

    _initialize() {
        if (!this.container) {
            console.error(`Container #${this.containerId} not found`);
            return;
        }

        // Set initial empty state
        this.showEmptyState();
    }

    /**
     * Show empty state when no file selected
     */
    showEmptyState() {
        this.container.innerHTML = `
            <div class="empty-state" style="padding: 2rem; text-align: center; color: #666;">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin: 0 auto 1rem;">
                    <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <h3 style="margin: 0 0 0.5rem; font-size: 1.2rem;">No File Selected</h3>
                <p style="margin: 0; font-size: 0.9rem;">Click on a bubble to view file details</p>
            </div>
        `;
    }

    /**
     * Display file details
     * @param {Object} fileData - File data from API
     */
    showFileDetails(fileData) {
        if (!fileData) {
            this.showEmptyState();
            return;
        }

        this.currentFile = fileData;

        const html = `
            <div class="file-details">
                <!-- Header -->
                <div class="file-header" style="padding: 1rem; border-bottom: 2px solid #DC143C; background: #f9f9f9;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.5rem;">📄</span>
                        <h2 style="margin: 0; font-size: 1.2rem; color: #333;">${this._getFileName(fileData.filepath)}</h2>
                    </div>
                    <p style="margin: 0.5rem 0 0; font-size: 0.85rem; color: #666; font-family: monospace;">
                        ${fileData.filepath}
                    </p>
                </div>
                
                <!-- Statistics -->
                <div class="file-stats" style="padding: 1rem; background: #fff;">
                    <h3 style="margin: 0 0 1rem; font-size: 1rem; color: #DC143C;">📊 Statistics</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; font-size: 0.9rem;">
                        <div>
                            <div style="color: #666; margin-bottom: 0.25rem;">Lines</div>
                            <div style="font-weight: bold; color: #333;">${fileData.lines || 0}</div>
                        </div>
                        <div>
                            <div style="color: #666; margin-bottom: 0.25rem;">Size</div>
                            <div style="font-weight: bold; color: #333;">${this._formatSize(fileData.size)}</div>
                        </div>
                        <div>
                            <div style="color: #666; margin-bottom: 0.25rem;">Functions</div>
                            <div style="font-weight: bold; color: #333;">${fileData.functions?.length || 0}</div>
                        </div>
                        <div>
                            <div style="color: #666; margin-bottom: 0.25rem;">Classes</div>
                            <div style="font-weight: bold; color: #333;">${fileData.classes?.length || 0}</div>
                        </div>
                    </div>
                </div>
                
                <!-- Functions -->
                ${this._renderFunctions(fileData.functions)}
                
                <!-- Classes -->
                ${this._renderClasses(fileData.classes)}
                
                <!-- Dependencies -->
                ${this._renderDependencies(fileData)}
            </div>
        `;

        this.container.innerHTML = html;

        // Attach event listeners
        this._attachEventListeners();
    }

    /**
     * Render functions list
     */
    _renderFunctions(functions) {
        if (!functions || functions.length === 0) {
            return '';
        }

        const functionItems = functions.map(func => `
            <div class="function-item" data-function="${func.name}" style="padding: 0.5rem; border-left: 3px solid #DC143C; margin-bottom: 0.5rem; background: #f9f9f9; cursor: pointer;">
                <div style="font-weight: 600; color: #333; margin-bottom: 0.25rem;">
                    ⚡ ${func.name}(${func.parameters.join(', ')})
                </div>
                <div style="font-size: 0.85rem; color: #666;">
                    Lines ${func.line_start}-${func.line_end}
                    ${func.is_async ? ' · <span style="color: #DC143C;">async</span>' : ''}
                    ${func.decorators && func.decorators.length > 0 ? ` · @${func.decorators.join(', @')}` : ''}
                </div>
                ${func.calls && func.calls.length > 0 ? `
                    <div style="font-size: 0.8rem; color: #999; margin-top: 0.25rem;">
                        Calls: ${func.calls.slice(0, 3).join(', ')}${func.calls.length > 3 ? '...' : ''}
                    </div>
                ` : ''}
            </div>
        `).join('');

        return `
            <div class="functions-section" style="padding: 1rem; border-top: 1px solid #e0e0e0;">
                <h3 style="margin: 0 0 1rem; font-size: 1rem; color: #DC143C;">🔧 Functions</h3>
                <div class="functions-list">
                    ${functionItems}
                </div>
            </div>
        `;
    }

    /**
     * Render classes list
     */
    _renderClasses(classes) {
        if (!classes || classes.length === 0) {
            return '';
        }

        const classItems = classes.map(cls => `
            <div class="class-item" style="padding: 0.5rem; border-left: 3px solid #3572A5; margin-bottom: 0.5rem; background: #f0f4f8;">
                <div style="font-weight: 600; color: #333; margin-bottom: 0.25rem;">
                    📦 ${cls.name}${cls.bases.length > 0 ? ` (${cls.bases.join(', ')})` : ''}
                </div>
                <div style="font-size: 0.85rem; color: #666;">
                    Lines ${cls.line_start}-${cls.line_end} · ${cls.methods.length} methods
                </div>
                ${cls.methods.length > 0 ? `
                    <div style="margin-top: 0.5rem; padding-left: 1rem; font-size: 0.85rem;">
                        ${cls.methods.slice(0, 5).map(m => `
                            <div style="color: #666; margin: 0.25rem 0;">
                                • ${m.name}(${m.parameters.join(', ')})
                            </div>
                        `).join('')}
                        ${cls.methods.length > 5 ? `<div style="color: #999;">+ ${cls.methods.length - 5} more...</div>` : ''}
                    </div>
                ` : ''}
            </div>
        `).join('');

        return `
            <div class="classes-section" style="padding: 1rem; border-top: 1px solid #e0e0e0;">
                <h3 style="margin: 0 0 1rem; font-size: 1rem; color: #DC143C;">📦 Classes</h3>
                <div class="classes-list">
                    ${classItems}
                </div>
            </div>
        `;
    }

    /**
     * Render dependencies section
     */
    _renderDependencies(fileData) {
        const deps = fileData.dependencies || {};
        const imports = deps.imports || [];
        const importedBy = deps.imported_by || [];

        if (imports.length === 0 && importedBy.length === 0) {
            return '';
        }

        return `
            <div class="dependencies-section" style="padding: 1rem; border-top: 1px solid #e0e0e0;">
                <h3 style="margin: 0 0 1rem; font-size: 1rem; color: #DC143C;">🔗 Dependencies</h3>
                
                ${imports.length > 0 ? `
                    <div style="margin-bottom: 1rem;">
                        <h4 style="margin: 0 0 0.5rem; font-size: 0.9rem; color: #666;">📥 Imports from:</h4>
                        <div class="imports-list">
                            ${imports.map(imp => `
                                <div class="import-item" data-file="${imp}" style="padding: 0.4rem; margin: 0.25rem 0; background: #f9f9f9; border-radius: 4px; font-size: 0.85rem; cursor: pointer; transition: background 0.2s;">
                                    ${this._getFileName(imp)}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${importedBy.length > 0 ? `
                    <div>
                        <h4 style="margin: 0 0 0.5rem; font-size: 0.9rem; color: #666;">📤 Imported by:</h4>
                        <div class="imported-by-list">
                            ${importedBy.map(imp => `
                                <div class="import-item" data-file="${imp}" style="padding: 0.4rem; margin: 0.25rem 0; background: #fff3f3; border-radius: 4px; font-size: 0.85rem; cursor: pointer; transition: background 0.2s;">
                                    ${this._getFileName(imp)}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Attach event listeners to interactive elements
     */
    _attachEventListeners() {
        // Function items
        const functionItems = this.container.querySelectorAll('.function-item');
        functionItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const funcName = e.currentTarget.dataset.function;
                if (this.onFunctionClick) {
                    const func = this.currentFile.functions.find(f => f.name === funcName);
                    this.onFunctionClick(func);
                }
            });

            // Hover effect
            item.addEventListener('mouseenter', (e) => {
                e.currentTarget.style.background = '#ffe6e6';
            });
            item.addEventListener('mouseleave', (e) => {
                e.currentTarget.style.background = '#f9f9f9';
            });
        });

        // Import items
        const importItems = this.container.querySelectorAll('.import-item');
        importItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const filepath = e.currentTarget.dataset.file;
                if (this.onImportClick) {
                    this.onImportClick(filepath);
                }
            });

            // Hover effect
            item.addEventListener('mouseenter', (e) => {
                e.currentTarget.style.background = '#ffd6d6';
            });
            item.addEventListener('mouseleave', (e) => {
                const isBg = e.currentTarget.closest('.imported-by-list') ? '#fff3f3' : '#f9f9f9';
                e.currentTarget.style.background = isBg;
            });
        });
    }

    /**
     * Get filename from full path
     */
    _getFileName(filepath) {
        if (!filepath) return '';
        const parts = filepath.split(/[/\\]/);
        return parts[parts.length - 1];
    }

    /**
     * Format file size
     */
    _formatSize(bytes) {
        if (!bytes) return '0 B';
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    }

    /**
     * Clear sidebar
     */
    clear() {
        this.currentFile = null;
        this.showEmptyState();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DetailsSidebar;
}
