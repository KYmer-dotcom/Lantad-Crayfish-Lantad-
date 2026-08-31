/**
 * Universal Table Enhancer: Real-time Search, Multi-Filter, Sorting & Pagination
 * Silay Aquaculture Management System
 */

class TableEnhancer {
    constructor(tableElement, options = {}) {
        this.table = typeof tableElement === 'string' ? document.querySelector(tableElement) : tableElement;
        if (!this.table) return;

        this.options = Object.assign({
            pageSize: 10,
            pageSizeOptions: [5, 10, 25, 50, 100],
            searchable: true,
            sortable: true,
            filterable: true,
            filterColumns: [], // [{ colIndex: 5, label: 'Status' }]
            searchPlaceholder: 'Search table records...',
            emptyMessage: 'No matching records found'
        }, options);

        this.tbody = this.table.querySelector('tbody');
        if (!this.tbody) return;

        // ONLY get direct child rows of this tbody, ignoring inner nested tables
        this.allRows = Array.from(this.tbody.children).filter(el => el.tagName === 'TR');
        // Group nested child rows if any (e.g. customer-orders-X)
        this.rowGroups = this.extractRowGroups();
        this.filteredGroups = [...this.rowGroups];

        this.currentPage = 1;
        this.pageSize = this.options.pageSize;
        this.searchQuery = '';
        this.columnFilters = {};
        this.currentSort = { colIndex: -1, direction: 'asc' };

        this.initDOM();
        this.render();
    }

    extractRowGroups() {
        const groups = [];
        let currentParent = null;

        this.allRows.forEach(row => {
            if (row.classList.contains('empty-table-row') || row.classList.contains('enhancer-empty-row')) {
                // Ignore empty placeholder row
                return;
            }

            const id = row.getAttribute('id') || '';
            const isChild = id.startsWith('customer-orders-') || 
                            row.classList.contains('child-row') || 
                            row.classList.contains('nested-row') ||
                            (row.querySelector('td[colspan]') && currentParent !== null);

            if (isChild) {
                if (currentParent) {
                    currentParent.children.push(row);
                }
            } else {
                currentParent = { parent: row, children: [], text: row.textContent.toLowerCase() };
                groups.push(currentParent);
            }
        });

        return groups;
    }

    initDOM() {
        // Wrap table in container
        this.container = document.createElement('div');
        this.container.className = 'enhanced-table-wrapper space-y-4';
        this.table.parentNode.insertBefore(this.container, this.table);

        // Header controls (Search, Filters, Page Size)
        this.controlsBar = document.createElement('div');
        this.controlsBar.className = 'flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl border border-white/10 bg-black/30 backdrop-blur-md';
        this.container.appendChild(this.controlsBar);

        // Left side: Search and Filters
        const leftBox = document.createElement('div');
        leftBox.className = 'flex flex-wrap items-center gap-3 flex-1 min-w-[280px]';

        if (this.options.searchable) {
            const searchContainer = document.createElement('div');
            searchContainer.className = 'relative flex-1 max-w-xs min-w-[200px]';
            searchContainer.innerHTML = `
                <input type="search" placeholder="${this.options.searchPlaceholder}" 
                    class="w-full rounded-xl border border-white/10 bg-black/50 px-4 py-2.5 pl-9 text-xs text-stone-100 placeholder-[#a0ac96] focus:border-[#cca43b] focus:outline-none focus:ring-1 focus:ring-[#cca43b] transition-all">
                <svg class="absolute left-3 top-3 h-3.5 w-3.5 text-[#a0ac96]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
            `;
            const searchInput = searchContainer.querySelector('input');
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value.toLowerCase().trim();
                this.currentPage = 1;
                this.applyFilters();
            });
            leftBox.appendChild(searchContainer);
        }

        // Auto-detect or use filter columns
        this.filterSelects = {};
        if (this.options.filterable && this.options.filterColumns.length > 0) {
            this.options.filterColumns.forEach(filterCol => {
                const selectContainer = document.createElement('div');
                selectContainer.className = 'relative';

                const uniqueValues = this.getUniqueColumnValues(filterCol.colIndex);
                if (uniqueValues.length > 1) {
                    let optionsHtml = `<option value="">All ${filterCol.label || 'Status'}</option>`;
                    uniqueValues.forEach(val => {
                        optionsHtml += `<option value="${val.toLowerCase()}">${val}</option>`;
                    });

                    selectContainer.innerHTML = `
                        <select class="rounded-xl border border-white/10 bg-black/50 px-3 py-2.5 text-xs font-bold text-stone-200 focus:border-[#cca43b] focus:outline-none cursor-pointer">
                            ${optionsHtml}
                        </select>
                    `;
                    const select = selectContainer.querySelector('select');
                    select.addEventListener('change', (e) => {
                        this.columnFilters[filterCol.colIndex] = e.target.value.toLowerCase();
                        this.currentPage = 1;
                        this.applyFilters();
                    });
                    this.filterSelects[filterCol.colIndex] = select;
                    leftBox.appendChild(selectContainer);
                }
            });
        }

        this.controlsBar.appendChild(leftBox);

        // Right side: Page size selector
        const rightBox = document.createElement('div');
        rightBox.className = 'flex items-center gap-2 text-xs text-[#a0ac96]';
        rightBox.innerHTML = `
            <span class="font-medium text-[11px] uppercase tracking-wider">Show</span>
            <select class="rounded-xl border border-white/10 bg-black/50 px-3 py-2 text-xs font-bold text-stone-200 focus:border-[#cca43b] focus:outline-none cursor-pointer">
                ${this.options.pageSizeOptions.map(size => `<option value="${size}" ${size === this.pageSize ? 'selected' : ''}>${size}</option>`).join('')}
            </select>
            <span class="font-medium text-[11px] uppercase tracking-wider">entries</span>
        `;
        const pageSizeSelect = rightBox.querySelector('select');
        pageSizeSelect.addEventListener('change', (e) => {
            this.pageSize = parseInt(e.target.value);
            this.currentPage = 1;
            this.render();
        });
        this.controlsBar.appendChild(rightBox);

        // Insert table into container
        this.container.appendChild(this.table);

        // Footer Pagination Bar
        this.paginationBar = document.createElement('div');
        this.paginationBar.className = 'flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-white/10 text-xs text-[#a0ac96]';
        this.container.appendChild(this.paginationBar);

        // Enable sorting on headers if enabled
        if (this.options.sortable) {
            const headers = this.table.querySelectorAll('thead th');
            headers.forEach((th, idx) => {
                th.classList.add('cursor-pointer', 'select-none', 'hover:text-white', 'transition-colors');
                th.title = 'Click to sort';
                th.addEventListener('click', () => {
                    this.sortByColumn(idx);
                });
            });
        }
    }

    getUniqueColumnValues(colIndex) {
        const values = new Set();
        this.rowGroups.forEach(group => {
            const cell = group.parent.children[colIndex];
            if (cell) {
                const text = cell.textContent.trim().replace(/\s+/g, ' ');
                if (text && text !== '-' && text.length < 30) {
                    values.add(text);
                }
            }
        });
        return Array.from(values).sort();
    }

    applyFilters() {
        this.filteredGroups = this.rowGroups.filter(group => {
            // Text search
            if (this.searchQuery && !group.text.includes(this.searchQuery)) {
                return false;
            }

            // Column filters
            for (const colIndex in this.columnFilters) {
                const targetVal = this.columnFilters[colIndex];
                if (targetVal) {
                    const cell = group.parent.children[colIndex];
                    if (!cell) return false;
                    const cellText = cell.textContent.trim().toLowerCase().replace(/\s+/g, ' ');
                    const words = cellText.split(/\s+/);
                    // Match full word or exact match (prevents 'paid' matching 'unpaid')
                    const isMatch = cellText === targetVal || words.includes(targetVal) || (cellText.includes(targetVal) && targetVal !== 'paid');
                    if (!isMatch) {
                        return false;
                    }
                }
            }

            return true;
        });

        this.render();
    }

    sortByColumn(colIndex) {
        if (this.currentSort.colIndex === colIndex) {
            this.currentSort.direction = this.currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.currentSort.colIndex = colIndex;
            this.currentSort.direction = 'asc';
        }

        const dir = this.currentSort.direction === 'asc' ? 1 : -1;

        this.filteredGroups.sort((a, b) => {
            const cellA = a.parent.children[colIndex] ? a.parent.children[colIndex].textContent.trim() : '';
            const cellB = b.parent.children[colIndex] ? b.parent.children[colIndex].textContent.trim() : '';

            // Clean currency or number
            const numA = parseFloat(cellA.replace(/[^0-9.-]+/g, ''));
            const numB = parseFloat(cellB.replace(/[^0-9.-]+/g, ''));

            if (!isNaN(numA) && !isNaN(numB)) {
                return (numA - numB) * dir;
            }

            return cellA.localeCompare(cellB) * dir;
        });

        this.render();
    }

    render() {
        const total = this.filteredGroups.length;
        const totalPages = Math.ceil(total / this.pageSize) || 1;
        if (this.currentPage > totalPages) this.currentPage = totalPages;

        const startIndex = (this.currentPage - 1) * this.pageSize;
        const endIndex = Math.min(startIndex + this.pageSize, total);

        // Update row visibility based on pagination
        const visibleGroups = this.filteredGroups.slice(startIndex, endIndex);
        const visibleSet = new Set(visibleGroups);

        this.rowGroups.forEach(group => {
            if (visibleSet.has(group)) {
                group.parent.style.display = '';
                group.children.forEach(child => {
                    // When parent is visible, let CSS classes (e.g. .hidden) toggle child display
                    child.style.display = child.classList.contains('hidden') ? 'none' : '';
                });
            } else {
                group.parent.style.display = 'none';
                group.children.forEach(child => {
                    child.style.display = 'none';
                });
            }
        });

        // Handle empty message
        let emptyRow = this.tbody.querySelector('.enhancer-empty-row');
        if (visibleGroups.length === 0) {
            if (!emptyRow) {
                emptyRow = document.createElement('tr');
                emptyRow.className = 'enhancer-empty-row';
                const colCount = this.table.querySelectorAll('thead th').length || 6;
                emptyRow.innerHTML = `
                    <td colspan="${colCount}" class="px-6 py-12 text-center text-sm text-stone-500 font-medium">
                        <div class="text-3xl mb-2">🔍</div>
                        <p class="text-stone-300 font-bold">${this.options.emptyMessage}</p>
                        <p class="text-xs text-[#a0ac96] mt-1">Try adjusting your search query or filter options.</p>
                    </td>
                `;
                this.tbody.appendChild(emptyRow);
            }
            emptyRow.style.display = '';
        } else if (emptyRow) {
            emptyRow.style.display = 'none';
        }

        // Render Pagination Footer
        this.renderPagination(startIndex, endIndex, total, totalPages);
    }

    renderPagination(startIndex, endIndex, total, totalPages) {
        const infoHtml = total > 0
            ? `Showing <span class="font-bold text-stone-200">${startIndex + 1}</span> to <span class="font-bold text-stone-200">${endIndex}</span> of <span class="font-bold text-[#cca43b]">${total}</span> entries`
            : `Showing 0 entries`;

        let paginationButtonsHtml = '';
        if (totalPages > 1) {
            paginationButtonsHtml = `
                <div class="flex items-center gap-1.5">
                    <button type="button" class="btn-prev px-3 py-1.5 rounded-xl border border-white/10 bg-black/40 text-xs font-bold text-stone-300 hover:text-white hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-all" ${this.currentPage === 1 ? 'disabled' : ''}>
                        ← Prev
                    </button>
            `;

            for (let p = 1; p <= totalPages; p++) {
                if (p === 1 || p === totalPages || (p >= this.currentPage - 1 && p <= this.currentPage + 1)) {
                    const isActive = p === this.currentPage;
                    paginationButtonsHtml += `
                        <button type="button" data-page="${p}" class="btn-page w-8 h-8 rounded-xl text-xs font-black transition-all ${isActive ? 'bg-[#cca43b] text-[#01140e] shadow-md shadow-[#cca43b]/20' : 'border border-white/10 bg-black/40 text-stone-300 hover:text-white hover:bg-white/10'}">
                            ${p}
                        </button>
                    `;
                } else if (p === this.currentPage - 2 || p === this.currentPage + 2) {
                    paginationButtonsHtml += `<span class="px-1 text-stone-500">...</span>`;
                }
            }

            paginationButtonsHtml += `
                    <button type="button" class="btn-next px-3 py-1.5 rounded-xl border border-white/10 bg-black/40 text-xs font-bold text-stone-300 hover:text-white hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-all" ${this.currentPage === totalPages ? 'disabled' : ''}>
                        Next →
                    </button>
                </div>
            `;
        }

        this.paginationBar.innerHTML = `
            <div class="text-[11px]">${infoHtml}</div>
            <div>${paginationButtonsHtml}</div>
        `;

        // Wire pagination clicks
        const prevBtn = this.paginationBar.querySelector('.btn-prev');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.render();
                }
            });
        }

        const nextBtn = this.paginationBar.querySelector('.btn-next');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (this.currentPage < totalPages) {
                    this.currentPage++;
                    this.render();
                }
            });
        }

        this.paginationBar.querySelectorAll('.btn-page').forEach(btn => {
            btn.addEventListener('click', () => {
                this.currentPage = parseInt(btn.getAttribute('data-page'));
                this.render();
            });
        });
    }
}

// Global initialization helper
window.TableEnhancer = TableEnhancer;
window.initTableEnhancer = function (selector, options) {
    const tables = document.querySelectorAll(selector);
    tables.forEach(table => {
        if (!table.dataset.enhanced) {
            table.dataset.enhanced = 'true';
            new TableEnhancer(table, options);
        }
    });
};

document.addEventListener('DOMContentLoaded', () => {
    // Auto-initialize any table with class .enhanced-table
    window.initTableEnhancer('.enhanced-table');
});
