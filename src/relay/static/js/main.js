function copyCommand(element) {
    const command = element.dataset.command
    const name = element.querySelector('h3').textContent

    navigator.clipboard.writeText(command).then(() => {
        showToast(name, command)
    })
}

function showToast(name, command) {
    const toast = document.createElement('div')
    const preview = command.length > 50 ? command.slice(0, 50) + '...' : command

    toast.className = 'toast'
    toast.innerHTML = `
    <i data-lucide="clipboard-check"></i>
    <div>
        <span class="toast-title">Copied to clipboard - ${name}</span>
        <span class="toast-preview">${preview}</span>
    </div>
    `

    document.body.appendChild(toast)

    lucide.createIcons()

    setTimeout(() => {
        toast.remove()
    }, 3000)
}