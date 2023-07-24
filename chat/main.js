

const ws = new WebSocket('ws://127.0.0.1:8080')

ws.onopen = () => {
    console.log('WebSocket connect')
}



formChat.addEventListener('submit', (e) => {
    e.preventDefault()
    ws.send(textField.value)
    textField.value = null
})



ws.onmessage = (e) => {
    console.log(e.data)
    text = e.data

    const elForMessage = document.createElement('div')
    const title = document.createElement('h3')
    const message = document.createElement('p')


    elForMessage.classList.add('message')
    title.textContent = text.split(':')[0]
    message.textContent = text.split(':')[1]

    elForMessage.appendChild(title)
    elForMessage.appendChild(message)
    // elForMessage.textContent = text
    messages.appendChild(elForMessage)
}