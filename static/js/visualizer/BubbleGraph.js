/**
 * Code Explorer - Bubble Graph Visualization
 * 
 * Interactive D3.js force-directed graph showing file dependencies
 * Features:
 * - Bubble nodes representing files
 * - Lines showing import relationships
 * - Zoom & pan navigation
 * - Click to show file details
 * - Search & filter capabilities
 */

class BubbleGraph {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = d3.select(`#${containerId}`);

        // Graph dimensions
        this.width = 0;
        this.height = 0;

        // SVG elements
        this.svg = null;
        this.g = null; // Main group for zoom/pan

        // D3 force simulation
        this.simulation = null;

        // Graph data
        this.nodes = [];
        this.edges = [];

        // UI elements (references)
        this.linkElements = null;
        this.nodeElements = null;
        this.textElements = null;

        // State
        this.selectedNode = null;
        this.highlightedNodes = new Set();

        // Callbacks
        this.onNodeClick = null;
        this.onNodeHover = null;

        this._initialize();
    }

    _initialize() {
        // Get container dimensions
        const rect = this.container.node().getBoundingClientRect();
        this.width = rect.width || 1200;
        this.height = rect.height || 800;

        // Create SVG
        this.svg = this.container
            .append('svg')
            .attr('width', '100%')
            .attr('height', '100%')
            .attr('viewBox', `0 0 ${this.width} ${this.height}`);

        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                this.g.attr('transform', event.transform);
            });

        this.svg.call(zoom);

        // Main group for all graph elements
        this.g = this.svg.append('g');

        // Create arrow marker for directed edges
        this.svg.append('defs').append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 20)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#999');

        // Initialize force simulation
        this.simulation = d3.forceSimulation()
            .force('link', d3.forceLink().id(d => d.id).distance(150))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(d => this._getNodeRadius(d) + 5));
    }

    /**
     * Render graph with given data
     * @param {Object} data - Graph data {nodes: [], edges: []}
     */
    render(data) {
        if (!data || !data.nodes || !data.edges) {
            console.error('Invalid graph data');
            return;
        }

        this.nodes = data.nodes;
        this.edges = data.edges;

        // Clear existing elements
        this.g.selectAll('*').remove();

        // Create links (edges)
        this.linkElements = this.g.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(this.edges)
            .enter()
            .append('line')
            .attr('class', 'link')
            .attr('stroke', '#999')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', 1.5)
            .attr('marker-end', 'url(#arrowhead)');

        // Create nodes (bubbles)
        const nodeGroups = this.g.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(this.nodes)
            .enter()
            .append('g')
            .attr('class', 'node')
            .call(this._dragBehavior());

        // Node circles
        this.nodeElements = nodeGroups.append('circle')
            .attr('r', d => this._getNodeRadius(d))
            .attr('fill', d => this._getNodeColor(d))
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .on('click', (event, d) => this._handleNodeClick(event, d))
            .on('mouseenter', (event, d) => this._handleNodeHover(event, d))
            .on('mouseleave', (event, d) => this._handleNodeLeave(event, d));

        // Node labels
        this.textElements = nodeGroups.append('text')
            .text(d => this._getNodeLabel(d))
            .attr('font-size', 12)
            .attr('dx', d => this._getNodeRadius(d) + 5)
            .attr('dy', 4)
            .attr('fill', '#333')
            .attr('pointer-events', 'none');

        // Update simulation
        this.simulation
            .nodes(this.nodes)
            .on('tick', () => this._ticked());

        this.simulation
            .force('link')
            .links(this.edges);

        // Restart simulation
        this.simulation.alpha(1).restart();
    }

    /**
     * Update positions on each simulation tick
     */
    _ticked() {
        // Update link positions
        this.linkElements
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        // Update node positions
        this.g.selectAll('.node')
            .attr('transform', d => `translate(${d.x},${d.y})`);
    }

    /**
     * Calculate node radius based on file size or importance
     */
    _getNodeRadius(node) {
        // Base radius on centrality score or file size
        const baseRadius = 10;
        const centralityBonus = (node.centrality || 0) * 20;

        return Math.max(baseRadius, baseRadius + centralityBonus);
    }

    /**
     * Get node color based on file type or metrics
     */
    _getNodeColor(node) {
        // Color by file type or language
        const colorMap = {
            'python': '#3572A5',
            'javascript': '#F1E05A',
            'typescript': '#2B7489',
            'default': '#DC143C' // Crimson theme
        };

        return colorMap[node.language] || colorMap.default;
    }

    /**
     * Get display label for node
     */
    _getNodeLabel(node) {
        // Show filename only (without path)
        const parts = node.id.split(/[/\\]/);
        return parts[parts.length - 1];
    }

    /**
     * Handle node click event
     */
    _handleNodeClick(event, node) {
        event.stopPropagation();

        // Update selection
        this.selectedNode = node;

        // Highlight connected nodes
        this._highlightConnections(node);

        // Trigger callback
        if (this.onNodeClick) {
            this.onNodeClick(node);
        }
    }

    /**
     * Handle node hover event
     */
    _handleNodeHover(event, node) {
        // Enlarge node slightly
        d3.select(event.currentTarget)
            .transition()
            .duration(200)
            .attr('r', this._getNodeRadius(node) * 1.2);

        // Trigger callback
        if (this.onNodeHover) {
            this.onNodeHover(node);
        }
    }

    /**
     * Handle node leave event
     */
    _handleNodeLeave(event, node) {
        // Return to normal size
        d3.select(event.currentTarget)
            .transition()
            .duration(200)
            .attr('r', this._getNodeRadius(node));
    }

    /**
     * Highlight node and its connections
     */
    _highlightConnections(node) {
        this.highlightedNodes.clear();
        this.highlightedNodes.add(node.id);

        // Find connected nodes
        this.edges.forEach(edge => {
            if (edge.source.id === node.id) {
                this.highlightedNodes.add(edge.target.id);
            }
            if (edge.target.id === node.id) {
                this.highlightedNodes.add(edge.source.id);
            }
        });

        // Update visual highlighting
        this.nodeElements
            .attr('opacity', d => this.highlightedNodes.has(d.id) ? 1 : 0.2)
            .attr('stroke-width', d => d.id === node.id ? 4 : 2);

        this.linkElements
            .attr('opacity', d =>
                d.source.id === node.id || d.target.id === node.id ? 1 : 0.1
            )
            .attr('stroke-width', d =>
                d.source.id === node.id || d.target.id === node.id ? 2.5 : 1.5
            );

        this.textElements
            .attr('opacity', d => this.highlightedNodes.has(d.id) ? 1 : 0.3);
    }

    /**
     * Clear all highlights
     */
    clearHighlights() {
        this.highlightedNodes.clear();
        this.selectedNode = null;

        this.nodeElements
            .attr('opacity', 1)
            .attr('stroke-width', 2);

        this.linkElements
            .attr('opacity', 0.6)
            .attr('stroke-width', 1.5);

        this.textElements
            .attr('opacity', 1);
    }

    /**
     * Search for nodes by name
     */
    searchNodes(query) {
        if (!query) {
            this.clearHighlights();
            return;
        }

        const lowerQuery = query.toLowerCase();
        const matches = this.nodes.filter(node =>
            node.id.toLowerCase().includes(lowerQuery)
        );

        if (matches.length > 0) {
            this._highlightConnections(matches[0]);
            return matches;
        }

        return [];
    }

    /**
     * Filter nodes by criteria
     */
    filterNodes(criteria) {
        // criteria: { language: 'python', minSize: 1000, etc. }
        const filtered = this.nodes.filter(node => {
            if (criteria.language && node.language !== criteria.language) {
                return false;
            }
            if (criteria.minSize && node.size < criteria.minSize) {
                return false;
            }
            if (criteria.maxSize && node.size > criteria.maxSize) {
                return false;
            }
            return true;
        });

        // Hide non-matching nodes
        this.nodeElements
            .attr('opacity', d => filtered.includes(d) ? 1 : 0.1);

        this.textElements
            .attr('opacity', d => filtered.includes(d) ? 1 : 0.1);

        return filtered;
    }

    /**
     * Reset view to default zoom/pan
     */
    resetView() {
        this.svg
            .transition()
            .duration(750)
            .call(
                d3.zoom().transform,
                d3.zoomIdentity
            );

        this.clearHighlights();
    }

    /**
     * Focus on specific node
     */
    focusNode(nodeId) {
        const node = this.nodes.find(n => n.id === nodeId);
        if (!node) return;

        // Calculate zoom transform to center on node
        const scale = 1.5;
        const x = -node.x * scale + this.width / 2;
        const y = -node.y * scale + this.height / 2;

        this.svg
            .transition()
            .duration(750)
            .call(
                d3.zoom().transform,
                d3.zoomIdentity.translate(x, y).scale(scale)
            );

        this._highlightConnections(node);
    }

    /**
     * Create drag behavior for nodes
     */
    _dragBehavior() {
        return d3.drag()
            .on('start', (event, d) => {
                if (!event.active) this.simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            })
            .on('drag', (event, d) => {
                d.fx = event.x;
                d.fy = event.y;
            })
            .on('end', (event, d) => {
                if (!event.active) this.simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            });
    }

    /**
     * Export graph as SVG
     */
    exportSVG() {
        const svgData = this.svg.node().outerHTML;
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.download = 'code-graph.svg';
        link.click();

        URL.revokeObjectURL(url);
    }

    /**
     * Destroy graph and clean up
     */
    destroy() {
        if (this.simulation) {
            this.simulation.stop();
        }
        this.container.selectAll('*').remove();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BubbleGraph;
}
