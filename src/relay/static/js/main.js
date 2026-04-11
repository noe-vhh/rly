const activeFilters = new Set()

function copyCommand(element) {
    const name = element.querySelector('h3').textContent
    const command = element.dataset.command
    const danger = element.dataset.danger

    if (danger === 'destructive') {
        showConfirmModal(
            name,
            'This action is destructive and may be difficult to reverse. Are you sure?',
            () => {
                navigator.clipboard.writeText(command).then(() => {
                    showToast(name, command, 'destructive')
                })
            },
            'Copy anyway'  // 👈 add this
        )
    } else {
        navigator.clipboard.writeText(command).then(() => {
            showToast(name, command, danger)
        })
    }
}

function showConfirmModal(title, message, onConfirm, confirmLabel = 'Confirm') {
    const overlay = document.createElement('div')
    overlay.className = 'modal-overlay'

    const modal = document.createElement('div')
    modal.className = 'modal'

    modal.innerHTML = `
        <div class="modal-header">
            <i data-lucide="triangle-alert"></i>
            <h3>Destructive action</h3>
        </div>
        <p>${title}</p>
        <p class="modal-warning">${message}</p>
        <div class="modal-buttons">
            <button class="btn-cancel">Cancel</button>
            <button class="btn-confirm">${confirmLabel}</button>
        </div>
    `

    overlay.appendChild(modal)
    document.body.appendChild(overlay)

    lucide.createIcons()

    overlay.querySelector('.btn-cancel').onclick = () => {
    document.body.removeChild(overlay)
    }
    
    overlay.querySelector('.btn-confirm').onclick = () => {
    document.body.removeChild(overlay)
    onConfirm()
    }
}

function showToast(name, command, danger) {
    const toast = document.createElement('div')
    const preview = command.length > 50 ? command.slice(0, 50) + '...' : command

    toast.className = 'toast'
    toast.classList.add(`toast-${danger}`)
    toast.innerHTML = `
    <i data-lucide="clipboard-check"></i>
    <div>
        <span class="toast-title">Copied to clipboard - ${name}</span>
        <span class="toast-preview">${preview}</span>
    </div>
    `

    const existingToast = document.querySelector('.toast')
    if (existingToast) {
    existingToast.style.animation = 'fadeOut 0.2s ease forwards'
    setTimeout(() => existingToast.remove(), 200)
    }

    document.body.appendChild(toast)

    lucide.createIcons()

    setTimeout(() => {
        toast.remove()
    }, 3000)
}

function filterCards(searchTerm) {
    const cards = document.querySelectorAll('.action-card')
    cards.forEach(card => {
        const name = card.querySelector('h3').textContent
        const command = card.dataset.command
        const description = card.querySelector('.action-description')?.textContent ?? ''

        const haystack = (name + ' ' + command + ' ' + description).toLowerCase()
        const matches = haystack.includes(searchTerm.toLowerCase())

        const cardTags = card.dataset.tags ? card.dataset.tags.split(',') : []
        const tagMatch = activeFilters.size === 0 || [...activeFilters].every(tag => cardTags.includes(tag))

        card.style.display = (matches && tagMatch) ? 'block' : 'none'
    })
    document.querySelectorAll('.tag, .badge-normal, .badge-warning, .badge-destructive').forEach(el => {
    const value = el.textContent.trim()
    if (activeFilters.has(value)) {
        el.classList.add('tag-active')
    } else {
        el.classList.remove('tag-active')
    }
    })
}

function selectCategory(element) {
    document.querySelector('.nav-item.active').classList.remove('active')
    element.classList.add('active')
    document.getElementById('search-input').value = ''
    document.querySelector('h1').textContent = element.textContent.trim()
    activeFilters.clear()
}

function toggleFilter(element, tag) {
    if (activeFilters.has(tag)) {
        activeFilters.delete(tag)
    } else {
        activeFilters.add(tag)
    }
    element.classList.toggle('tag-active')
    filterCards(document.getElementById('search-input').value)
}

function addCategory() {
    const nav = document.querySelector('.sidebar-nav')

    const input = document.createElement('input')
    input.className = 'nav-item nav-input'
    input.placeholder = 'Category name...'

    nav.appendChild(input)

    input.focus()

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const name = input.value.trim()
            if (!name) return

            fetch('/api/categories', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name })
            }).then(() => {
                htmx.ajax('GET', '/api/categories', {
                    target: '#sidebar-categories',
                    swap: 'innerHTML'
                })
            })

            nav.removeChild(input)
        }

        if (e.key === 'Escape') {
            nav.removeChild(input)
        }
    })
}

function deleteCategory(id, name) {
    showConfirmModal(
        `Delete "${name}"`,
        'This category will be removed. Actions in it will not be deleted.',
        () => {
            fetch(`/api/categories/${id}`, { method: 'DELETE' })
                .then(() => {
                    htmx.ajax('GET', '/api/categories', {
                        target: '#sidebar-categories',
                        swap: 'innerHTML'
                    })
                })
        },
        'Delete'
    )
}

document.body.addEventListener('htmx:afterSwap', () => {
    lucide.createIcons()
})
