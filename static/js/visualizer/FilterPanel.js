/**
 * Filter Panel - Search and Filter Controls
 * 
 * Provides UI controls for:
 * - Search by filename
 * - Filter by language
 * - Filter by size
 * - Filter by dependency count
 */

class FilterPanel {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);

        // State
        this.filters = {
            search: '',
            language: 'all',
            minSize: 0,
            maxSize: Infinity
        };

        // Callbacks
        this.onFilterChange = null;
        this.onSearchChange = null;

        this._initialize();
    }

    _initialize() {
        if (!this.container) {
            console.error(`Container #${this.containerId} not found`);
            return;
        }

        this._render();
        this._attachEventListeners();
    }

    _render() {
        this.container.innerHTML = `
            <div class="filter-panel" style="padding: 1rem; background: #f9f9f9; border-radius: 8px;">
                <!-- Search -->
                <div class="filter-group" style="margin-bottom: 1rem;">
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 600; color: #333; font-size: 0.9rem;">
                        🔍 Search Files
                    </label>
                    <input 
                        type="text" 
                        id="search-input" 
                        placeholder="Type filename..."
                        style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem;"
                    />
                </div>
                
                <!-- Language Filter -->
                <div class="filter-group" style="margin-bottom: 1rem;">
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 600; color: #333; font-size: 0.9rem;">
                        🔤 Language
                    </label>
                    <select 
                        id="language-filter"
                        style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem;"
                    >
                        <option value="all">All Languages</option>
                        <option value="python">Python</option>
                        <option value="javascript">JavaScript</option>
                        <option value="typescript">TypeScript</option>
                    </select>
                </div>
                
                <!-- Size Filter -->
                <div class="filter-group" style="margin-bottom: 1rem;">
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 600; color: #333; font-size: 0.9rem;">
                        📏 File Size
                    </label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                        <div>
                            <input 
                                type="number" 
                                id="min-size" 
                                placeholder="Min (KB)"
                                style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;"
                            />
                        </div>
                        <div>
                            <input 
                                type="number" 
                                id="max-size" 
                                placeholder="Max (KB)"
                                style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;"
                            />
                        </div>
                    </div>
                </div>
                
                <!-- Action Buttons -->
                <div class="filter-actions" style="display: flex; gap: 0.5rem; margin-top: 1.5rem;">
                    <button 
                        id="apply-filters"
                        style="flex: 1; padding: 0.6rem; background: #DC143C; color: white; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; font-size: 0.9rem;"
                    >
                        Apply Filters
                    </button>
                    <button 
                        id="reset-filters"
                        style="flex: 1; padding: 0.6rem; background: #666; color: white; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; font-size: 0.9rem;"
                    >
                        Reset
                    </button>
                </div>
            </div>
        `;
    }

    _attachEventListeners() {
        // Search input with debounce
        const searchInput = this.container.querySelector('#search-input');
        let searchTimeout;

        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.filters.search = e.target.value;
                if (this.onSearchChange) {
                    this.onSearchChange(this.filters.search);
                }
            }, 300); // Debounce 300ms
        });

        // Apply filters button
        const applyBtn = this.container.querySelector('#apply-filters');
        applyBtn.addEventListener('click', () => {
            this._collectFilters();
            if (this.onFilterChange) {
                this.onFilterChange(this.filters);
            }
        });

        // Reset filters button
        const resetBtn = this.container.querySelector('#reset-filters');
        resetBtn.addEventListener('click', () => {
            this._resetFilters();
        });

        // Hover effects for buttons
        [applyBtn, resetBtn].forEach(btn => {
            btn.addEventListener('mouseenter', (e) => {
                e.target.style.opacity = '0.8';
            });
            btn.addEventListener('mouseleave', (e) => {
                e.target.style.opacity = '1';
            });
        });
    }

    _collectFilters() {
        const languageFilter = this.container.querySelector('#language-filter');
        const minSize = this.container.querySelector('#min-size');
        const maxSize = this.container.querySelector('#max-size');

        this.filters.language = languageFilter.value;
        this.filters.minSize = minSize.value ? parseInt(minSize.value) * 1024 : 0;
        this.filters.maxSize = maxSize.value ? parseInt(maxSize.value) * 1024 : Infinity;
    }

    _resetFilters() {
        // Reset state
        this.filters = {
            search: '',
            language: 'all',
            minSize: 0,
            maxSize: Infinity
        };

        // Reset UI
        this.container.querySelector('#search-input').value = '';
        this.container.querySelector('#language-filter').value = 'all';
        this.container.querySelector('#min-size').value = '';
        this.container.querySelector('#max-size').value = '';

        // Trigger callback
        if (this.onFilterChange) {
            this.onFilterChange(this.filters);
        }
    }

    /**
     * Get current filter state
     */
    getFilters() {
        this._collectFilters();
        return { ...this.filters };
    }

    /**
     * Set filters programmatically
     */
    setFilters(filters) {
        if (filters.search !== undefined) {
            this.filters.search = filters.search;
            this.container.querySelector('#search-input').value = filters.search;
        }

        if (filters.language !== undefined) {
            this.filters.language = filters.language;
            this.container.querySelector('#language-filter').value = filters.language;
        }

        if (filters.minSize !== undefined) {
            this.filters.minSize = filters.minSize;
            this.container.querySelector('#min-size').value = Math.round(filters.minSize / 1024);
        }

        if (filters.maxSize !== undefined) {
            this.filters.maxSize = filters.maxSize;
            this.container.querySelector('#max-size').value = Math.round(filters.maxSize / 1024);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FilterPanel;
}
