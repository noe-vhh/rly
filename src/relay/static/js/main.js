function copyCommand(element) {
    const name = element.querySelector('h3').textContent
    const command = element.dataset.command
    const danger = element.dataset.danger

    if (danger === 'destructive') {
        showConfirmModal(name, command)
    } else {
        navigator.clipboard.writeText(command).then(() => {
            showToast(name, command, danger)
        })
    }
}

function showConfirmModal(name, command) {
    const overlay = document.createElement('div')
    overlay.className = 'modal-overlay'

    const modal = document.createElement('div')
    modal.className = 'modal'

    modal.innerHTML = `
        <div class="modal-header">
            <i data-lucide="triangle-alert"></i>
            <h3>Destructive action</h3>
        </div>
        <p>${name}</p>
        <p class="modal-warning">This action is destructive and may be difficult to reverse. Are you sure?</p>
        <div class="modal-buttons">
            <button class="btn-cancel">Cancel</button>
            <button class="btn-confirm">Copy anyway</button>
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
    navigator.clipboard.writeText(command).then(() => {
        showToast(name, command, 'destructive')
    })
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
        card.style.display = matches ? 'block' : 'none'
    })
}

function selectCategory(element) {
    document.querySelector('.nav-item.active').classList.remove('active')
    element.classList.add('active')
    document.getElementById('search-input').value = ''
    document.querySelector('h1').textContent = element.textContent.trim()
}