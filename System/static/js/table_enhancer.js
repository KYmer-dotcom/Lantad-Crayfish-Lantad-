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
                            id.startsWith('details-') ||
                            row.classList.contains('child-row') || 
                            row.classList.contains('nested-row') ||
                            (row.querySelector('td[colspan]') && currentParent !== null);

            if (isChild) {
                if (currentParent) {
                    currentParent.children.push(row);
                    currentParent.text += ' ' + row.textContent.toLowerCase();
                }
            } else {
                currentParent = { parent: row, children: [], text: row.textContent.toLowerCase() };
                groups.push(currentParent);
            }
        });

        return groups;
    }

    initDOM() {
        // Find if table is wrapped in an overflow container
        const parent = this.table.parentElement;
        const isParentOverflow = parent && (parent.classList.contains('overflow-x-auto') || parent.classList.contains('overflow-auto'));
        
        // Find top-level table card or container if any
        let cardContainer = isParentOverflow ? parent.parentElement : parent;
        const isCard = cardContainer && (
            cardContainer.classList.contains('border') ||
            cardContainer.classList.contains('rounded-lg') ||
            cardContainer.classList.contains('rounded-xl') ||
            cardContainer.classList.contains('rounded-2xl') ||
            cardContainer.classList.contains('rounded-3xl') ||
            cardContainer.classList.contains('bg-black/20') ||
            cardContainer.classList.contains('glass-card')
        ) && cardContainer.children.length === 1;

        // Container wrapper
        this.container = document.createElement('div');
        this.container.className = 'enhanced-table-wrapper space-y-4';

        // Header controls (Search, Filters, Page Size)
        this.controlsBar = document.createElement('div');
        this.controlsBar.className = 'flex flex-wrap items-center justify-between gap-4 p-3.5 sm:p-4 rounded-xl border border-white/10 bg-black/30 backdrop-blur-md';
        this.container.appendChild(this.controlsBar);

        // Left side: Search and Filters
        const leftBox = document.createElement('div');
        leftBox.className = 'flex flex-wrap items-center gap-3 flex-1 min-w-[240px]';

        if (this.options.searchable) {
            const searchContainer = document.createElement('div');
            searchContainer.className = 'relative flex-1 max-w-xs min-w-[200px]';
            searchContainer.innerHTML = `
                <input type="search" placeholder="${this.options.searchPlaceholder}" 
                    class="w-full rounded-lg border border-white/10 bg-black/40 px-3.5 py-2 pl-9 text-xs text-white placeholder-[#a0ac96] focus:border-[#cca43b] focus:outline-none focus:ring-1 focus:ring-[#cca43b] transition-all">
                <svg class="absolute left-3 top-2.5 h-3.5 w-3.5 text-[#a0ac96]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
                        <select class="rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-xs font-bold text-stone-200 focus:border-[#cca43b] focus:outline-none cursor-pointer">
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
        rightBox.className = 'flex items-center gap-2 text-xs text-[#a0ac96] shrink-0';
        rightBox.innerHTML = `
            <span class="font-bold text-[10px] uppercase tracking-wider text-[#a0ac96]">Show</span>
            <select class="rounded-lg border border-white/10 bg-black/40 px-2.5 py-1.5 text-xs font-bold text-white focus:border-[#cca43b] focus:outline-none cursor-pointer">
                ${this.options.pageSizeOptions.map(size => `<option value="${size}" ${size === this.pageSize ? 'selected' : ''}>${size}</option>`).join('')}
            </select>
            <span class="font-bold text-[10px] uppercase tracking-wider text-[#a0ac96]">entries</span>
        `;
        const pageSizeSelect = rightBox.querySelector('select');
        pageSizeSelect.addEventListener('change', (e) => {
            this.pageSize = parseInt(e.target.value);
            this.currentPage = 1;
            this.render();
        });
        this.controlsBar.appendChild(rightBox);

        // Footer Pagination Bar with proper padding and styling
        this.paginationBar = document.createElement('div');
        this.paginationBar.className = 'flex flex-col items-center justify-center gap-3 px-6 py-4 border-t border-white/10 bg-white/[0.02] text-xs text-[#a0ac96] select-none text-center';

        // Mount table and pagination cleanly
        if (isCard) {
            cardContainer.parentNode.insertBefore(this.container, cardContainer);
            this.container.appendChild(this.controlsBar);
            this.container.appendChild(cardContainer);
            cardContainer.appendChild(this.paginationBar);
        } else if (isParentOverflow) {
            parent.parentNode.insertBefore(this.container, parent);
            this.container.appendChild(this.controlsBar);

            const card = document.createElement('div');
            card.className = 'overflow-hidden rounded-lg border border-white/10 bg-black/20';
            card.appendChild(parent);
            card.appendChild(this.paginationBar);
            this.container.appendChild(card);
        } else {
            this.table.parentNode.insertBefore(this.container, this.table);
            this.container.appendChild(this.controlsBar);

            const card = document.createElement('div');
            card.className = 'overflow-hidden rounded-lg border border-white/10 bg-black/20';
            const scroll = document.createElement('div');
            scroll.className = 'overflow-x-auto';
            scroll.appendChild(this.table);
            card.appendChild(scroll);
            card.appendChild(this.paginationBar);
            this.container.appendChild(card);
        }

        // Enable sorting on headers if enabled
        if (this.options.sortable) {
            const headers = this.table.querySelectorAll('thead th');
            headers.forEach((th, idx) => {
                th.classList.add('cursor-pointer', 'select-none', 'hover:text-white', 'transition-colors');
                th.removeAttribute('title');
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

        // Keep DOM rows ordered according to current filter/sort and keep children adjacent to parents
        visibleGroups.forEach(group => {
            this.tbody.appendChild(group.parent);
            group.children.forEach(child => {
                this.tbody.appendChild(child);
            });
        });

        this.rowGroups.forEach(group => {
            if (visibleSet.has(group)) {
                group.parent.style.display = '';
                group.children.forEach(child => {
                    // When parent is visible, remove inline display override so CSS .hidden or user toggle works
                    child.style.display = '';
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
        let pagesHtml = '';
        for (let p = 1; p <= totalPages; p++) {
            if (p === 1 || p === totalPages || (p >= this.currentPage - 1 && p <= this.currentPage + 1)) {
                const isActive = p === this.currentPage;
                if (isActive) {
                    pagesHtml += `
                        <span class="h-8 w-8 rounded-full bg-[#cca43b] text-[#01140e] font-black text-xs flex items-center justify-center shadow-md select-none">
                            ${p}
                        </span>
                    `;
                } else {
                    pagesHtml += `
                        <button type="button" data-page="${p}" class="btn-page text-xs font-black text-[#a0ac96] hover:text-white transition-colors cursor-pointer px-2 py-1 select-none">
                            ${p}
                        </button>
                    `;
                }
            } else if (p === this.currentPage - 2 || p === this.currentPage + 2) {
                pagesHtml += `<span class="px-1 text-[#a0ac96]/40 font-bold select-none">...</span>`;
            }
        }

        const paginationHtml = `
            <div class="flex items-center justify-center gap-6 sm:gap-8 w-full select-none py-1">
                <!-- Previous -->
                <button type="button" class="btn-prev inline-flex items-center gap-2 font-black uppercase tracking-[0.25em] text-xs transition-colors ${this.currentPage === 1 ? 'text-white/20 cursor-not-allowed opacity-40' : 'text-[#a0ac96] hover:text-white cursor-pointer'}" ${this.currentPage === 1 ? 'disabled' : ''}>
                    <span>&larr;</span>
                    <span>PREV</span>
                </button>

                <!-- Page Numbers -->
                <div class="flex items-center gap-4 sm:gap-6">
                    ${pagesHtml}
                </div>

                <!-- Next -->
                <button type="button" class="btn-next inline-flex items-center gap-2 font-black uppercase tracking-[0.25em] text-xs transition-colors ${this.currentPage === totalPages ? 'text-white/20 cursor-not-allowed opacity-40' : 'text-[#a0ac96] hover:text-white cursor-pointer'}" ${this.currentPage === totalPages ? 'disabled' : ''}>
                    <span>NEXT</span>
                    <span>&rarr;</span>
                </button>
            </div>
        `;

        this.paginationBar.style.display = 'flex';
        this.paginationBar.innerHTML = paginationHtml;

        // Wire pagination clicks
        const prevBtn = this.paginationBar.querySelector('.btn-prev');
        if (prevBtn && this.currentPage > 1) {
            prevBtn.addEventListener('click', () => {
                this.currentPage--;
                this.render();
            });
        }

        const nextBtn = this.paginationBar.querySelector('.btn-next');
        if (nextBtn && this.currentPage < totalPages) {
            nextBtn.addEventListener('click', () => {
                this.currentPage++;
                this.render();
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
