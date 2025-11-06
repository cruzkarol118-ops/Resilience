class ChatBot {
    constructor() {
        this.isOpen = false;
        this.isProcessing = false;
        this.init();
    }

    init() {
        this.createWidget();
        this.bindEvents();
        this.addWelcomeMessage();
    }

    createWidget() {
        // Remover chatbot existente si hay uno
        const existingChatbot = document.getElementById('chatbot-widget');
        if (existingChatbot) {
            existingChatbot.remove();
        }

        const chatbotHTML = `
            <div id="chatbot-widget">
                <div id="chatbot-toggle">
                    <i class="fas fa-comments"></i>
                </div>
                <div id="chatbot-container">
                    <div id="chatbot-header">
                        <h4>🤖 Asistente Virtual</h4>
                        <button id="chatbot-close"><i class="fas fa-times"></i></button>
                    </div>
                    <div id="chatbot-messages"></div>
                    <div id="chatbot-input">
                        <input type="text" id="chatbot-text" placeholder="Escribe tu mensaje..." autocomplete="off">
                        <button id="chatbot-send"><i class="fas fa-paper-plane"></i></button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
    }

    bindEvents() {
        document.getElementById('chatbot-toggle').addEventListener('click', (e) => {
            e.stopPropagation(); // Evitar que el clic se propague al documento
            this.toggleChat();
        });
        document.getElementById('chatbot-close').addEventListener('click', (e) => {
             e.stopPropagation();
            this.toggleChat();
        });
        document.getElementById('chatbot-send').addEventListener('click', () => this.sendMessage());
        
        const textInput = document.getElementById('chatbot-text');
        textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isProcessing) {
                this.sendMessage();
            }
        });
        
        // Clic dentro del contenedor del chatbot no debe cerrarlo
        document.getElementById('chatbot-container').addEventListener('click', (e) => {
            e.stopPropagation();
        });

        // Cerrar chatbot al hacer clic fuera
        document.addEventListener('click', (e) => {
            const chatbot = document.getElementById('chatbot-widget');
            // Si el chatbot está abierto Y el clic NO fue en el botón de toggle
            if (this.isOpen && !chatbot.contains(e.target)) {
                 // Verificamos que el clic no sea en el toggle
                if (e.target.closest('#chatbot-toggle') === null) {
                    this.toggleChat();
                }
            }
        });
    }

    addWelcomeMessage() {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (messagesContainer) {
            const welcomeMsg = document.createElement('div');
            welcomeMsg.className = 'message bot-message';
            welcomeMsg.innerHTML = `
                <strong>¡Bienvenido a RESILIENCE! 👋</strong><br><br>
                Soy tu asistente virtual. Escribe 'Hola' para ver tus opciones personalizadas.
                <br><br>
                <em>¿En qué puedo ayudarte hoy?</em>
            `;
            messagesContainer.appendChild(welcomeMsg);
        }
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const container = document.getElementById('chatbot-container');
        const toggleBtn = document.getElementById('chatbot-toggle');
        
        if (this.isOpen) {
            container.style.display = 'flex';
            container.style.flexDirection = 'column';
            setTimeout(() => { // Pequeño delay para que el focus funcione
                 document.getElementById('chatbot-text').focus();
            }, 100);
            toggleBtn.innerHTML = '<i class="fas fa-times"></i>';
            toggleBtn.style.background = '#dc3545';
        } else {
            container.style.display = 'none';
            toggleBtn.innerHTML = '<i class="fas fa-comments"></i>';
            toggleBtn.style.background = 'linear-gradient(135deg, #6f3be6, #8a5de8)';
        }
    }

    async sendMessage() {
        if (this.isProcessing) return;

        const input = document.getElementById('chatbot-text');
        const message = input.value.trim();
        
        if (!message) return;

        this.isProcessing = true;
        this.addUserMessage(message);
        input.value = '';
        input.disabled = true;

        // Mostrar indicador de typing
        this.showTyping();

        try {
            const response = await fetch('/chatbot/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            if (response.status === 401 || response.status === 403) {
                 this.addBotMessage('Debes iniciar sesión para usar el chat.', 'error');
                 setTimeout(() => window.location.href = '/index1', 2000); // Redirigir al login
                 return;
            }

            const data = await response.json();
            this.hideTyping();
            
            if (data.success) {
                this.addBotMessage(data.response);
                if (data.actions && data.actions.length > 0) {
                    // Si la acción es única y no requiere botones, ejecutarla
                    if (data.actions.length === 1 && data.actions[0].type !== 'redirect') {
                        this.handleQuickAction(data.actions[0]);
                    } else {
                        // Mostrar botones de acción rápida
                        this.showQuickActions(data.actions);
                    }
                }
            } else {
                this.addBotMessage(data.response || '❌ Lo siento, hubo un error procesando tu solicitud.', 'error');
            }
        } catch (error) {
            console.error('Chatbot error:', error);
            this.hideTyping();
            this.addBotMessage('⚠️ Error de conexión. Por favor intenta nuevamente.', 'error');
        } finally {
            this.isProcessing = false;
            input.disabled = false;
            input.focus();
        }
    }

    addUserMessage(message) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.textContent = message;
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addBotMessage(message, type = 'normal') {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message bot-message ${type === 'error' ? 'error-message' : type === 'info' ? 'info-message' : ''}`;
        messageDiv.innerHTML = message; // Usamos innerHTML para renderizar <strong>, <br>, etc.
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showQuickActions(actions) {
        // Remover acciones rápidas anteriores
        document.querySelectorAll('.quick-actions').forEach(el => el.remove());

        const messagesContainer = document.getElementById('chatbot-messages');
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'quick-actions';
        
        actions.forEach(action => {
            const button = document.createElement('button');
            button.className = 'quick-action-btn';
            button.innerHTML = action.text; // El backend nos da el texto
            
            // Adjuntamos un 'click listener' que llama a handleQuickAction
            button.onclick = () => {
                // Deshabilitar botones después del clic
                actionsDiv.querySelectorAll('button').forEach(btn => btn.disabled = true);
                this.handleQuickAction(action);
            };
            actionsDiv.appendChild(button);
        });
        
        messagesContainer.appendChild(actionsDiv);
        this.scrollToBottom();
    }

    /**
     * Manejador central para todas las acciones de los botones.
     */
    handleQuickAction(action) {
        // Remover botones de acción rápida
        document.querySelectorAll('.quick-actions').forEach(el => el.remove());

        // Simular que el usuario 'dijo' la acción
        this.addUserMessage(action.text);

        switch (action.type) {
            case 'redirect':
                this.addBotMessage(`¡Claro! Te estoy redirigiendo a: ${action.text}...`);
                window.location.href = action.url;
                break;
            
            // Casos de Estudiante (Funciones Reales)
            case 'fetch_active_citas':
                this.consultarCitasUsuario();
                break;
            case 'fetch_historial':
                this.consultarHistorialUsuario();
                break;
            case 'fetch_pendientes':
                this.consultarPendientesCalificar();
                break;
            case 'prompt_cancel':
                // Esta acción la genera el backend al detectar 'cancelar'
                this.solicitarCancelacion();
                break;
            case 'exec_cancel':
                // Esta acción la genera el botón "Sí, cancelar"
                this.confirmarCancelacion();
                break;
            case 'abort_cancel':
                // Esta acción la genera el botón "No, conservar"
                this.addBotMessage('Entendido. No se ha cancelado nada. 👍');
                break;

            // Caso de Ayuda (vuelve a enviar el texto al backend)
            case 'ayuda':
                this.sendQuickActionMessage('ayuda');
                break;
            
            default:
                // Si el backend envía un tipo desconocido, lo enviamos de vuelta
                this.sendQuickActionMessage(action.text);
        }
    }

    /**
     * Envía un mensaje al backend SIN mostrarlo como un mensaje de usuario (usado para 'ayuda')
     */
    async sendQuickActionMessage(message) {
        this.isProcessing = true;
        this.showTyping();

        try {
            const response = await fetch('/chatbot/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();
            this.hideTyping();
            
            if (data.success) {
                this.addBotMessage(data.response);
                if (data.actions && data.actions.length > 0) {
                    this.showQuickActions(data.actions);
                }
            }
        } catch (error) {
            this.hideTyping();
            this.addBotMessage('❌ Error al procesar la acción.', 'error');
        } finally {
            this.isProcessing = false;
        }
    }

    // --- Funciones de Estudiante ---

    async consultarCitasUsuario() {
        this.showTyping();
        try {
            const response = await fetch('/chatbot/mis_citas');
            const data = await response.json();
            this.hideTyping();
            
            if (data.success && data.citas.length > 0) {
                let mensaje = '<strong>📅 Tu cita activa es:</strong><br><br>';
                data.citas.forEach(cita => {
                    mensaje += `
                        <strong>${cita.fecha}</strong> a las <strong>${cita.hora}</strong><br>
                        👨‍⚕️ <em>${cita.psicologo}</em><br>
                        📝 Estado: <strong>${cita.estado}</strong><br>
                        ${cita.ubicacion ? `📍 ${cita.ubicacion}<br>` : '📍 Ubicación pendiente.'}
                        <br>
                    `;
                });
                this.addBotMessage(mensaje);
                this.showQuickActions([
                    {'type': 'prompt_cancel', 'text': '🚫 Cancelar esta cita'}
                ]);
            } else {
                this.addBotMessage('📭 No tienes ninguna cita activa (Solicitada o Confirmada) en este momento.', 'info');
                this.showQuickActions([
                    {'type': 'redirect', 'text': '📅 Agendar una nueva cita', 'url': '/est_agendar'}
                ]);
            }
        } catch (error) {
            this.hideTyping();
            this.addBotMessage('❌ Error al consultar tus citas.', 'error');
        }
    }

    async consultarHistorialUsuario() {
        this.showTyping();
        try {
            const response = await fetch('/chatbot/mi_historial');
            const data = await response.json();
            this.hideTyping();
            
            if (data.success && data.citas.length > 0) {
                let mensaje = '<strong>📚 Tu historial de últimas 5 citas:</strong><br><br>';
                data.citas.forEach((cita, index) => {
                    mensaje += `
                        <strong>${index + 1}. ${cita.fecha}</strong> (${cita.hora})<br>
                        👨‍⚕️ <em>${cita.psicologo}</em><br>
                        Estado: <strong>${cita.estado}</strong><br><br>
                    `;
                });
                this.addBotMessage(mensaje);
            } else {
                this.addBotMessage('📭 No tienes historial de citas (Realizadas o Canceladas).', 'info');
            }
        } catch (error) {
            this.hideTyping();
            this.addBotMessage('❌ Error al consultar tu historial.', 'error');
        }
    }

    async consultarPendientesCalificar() {
        this.showTyping();
        try {
            const response = await fetch('/chatbot/citas_pendientes_calificar');
            const data = await response.json();
            this.hideTyping();
            
            if (data.success && data.count > 0) {
                this.addBotMessage(`¡Buenas noticias! Tienes <strong>${data.count}</strong> cita(s) realizadas pendientes por calificar. Tu opinión es muy importante.`);
                this.showQuickActions([
                     {'type': 'redirect', 'text': '⭐ Ir a calificar ahora', 'url': '/estudiante/historial'}
                ]);
            } else {
                this.addBotMessage('👍 Estás al día. No tienes citas pendientes por calificar.', 'info');
            }
        } catch (error) {
            this.hideTyping();
            this.addBotMessage('❌ Error al consultar tus citas pendientes.', 'error');
        }
    }

    solicitarCancelacion() {
        // El backend ya envió el mensaje "Estás seguro?".
        // Esta función solo muestra los botones de confirmación.
        this.showQuickActions([
            {'type': 'exec_cancel', 'text': 'Sí, estoy seguro, cancelar'},
            {'type': 'abort_cancel', 'text': 'No, conservar mi cita'}
        ]);
    }

    async confirmarCancelacion() {
        this.showTyping();
        try {
            const response = await fetch('/chatbot/cancelar_mi_cita', { method: 'POST' });
            const data = await response.json();
            this.hideTyping();
            
            if (data.success) {
                this.addBotMessage(`✅ ${data.message}`, 'info');
            } else {
                this.addBotMessage(`⚠️ ${data.message}`, 'error');
                // Si falla (ej. no tenía cita), le ofrecemos agendar
                if (data.message.includes('No se encontró')) {
                    this.showQuickActions([
                        {'type': 'redirect', 'text': '📅 Agendar una cita', 'url': '/est_agendar'}
                    ]);
                }
            }
        } catch (error) {
            this.hideTyping();
            this.addBotMessage('❌ Ocurrió un error de red al intentar cancelar.', 'error');
        }
    }


    showTyping() {
        const messagesContainer = document.getElementById('chatbot-messages');
        // Evitar múltiples indicadores
        if (document.getElementById('typing-indicator')) return;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTyping() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
}

// Inicializar el chatbot cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Pequeño delay para asegurar que todo esté cargado
    setTimeout(() => {
        // Asegurarnos que solo haya una instancia
        if (!document.getElementById('chatbot-widget')) {
            new ChatBot();
        }
    }, 1000);
});