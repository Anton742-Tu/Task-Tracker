// Основные функции JavaScript для Task Tracker

document.addEventListener('DOMContentLoaded', function() {

    // 1. Форматирование дат
    formatDates();

    // 2. Подсветка активной навигации
    highlightActiveNav();

    // 3. Добавление анимаций
    addAnimations();

    // 4. Инициализация всплывающих подсказок
    initTooltips();

    // 5. Обработка статусов
    updateStatusColors();
});

function formatDates() {
    // Форматируем все элементы с классами date и time
    const dateElements = document.querySelectorAll('.date-time, .date-only, .time-only');

    dateElements.forEach(element => {
        const dateString = element.textContent;
        if (dateString) {
            try {
                const date = new Date(dateString);
                if (!isNaN(date)) {
                    let formattedDate;

                    if (element.classList.contains('date-only')) {
                        formattedDate = date.toLocaleDateString('ru-RU', {
                            day: '2-digit',
                            month: 'long',
                            year: 'numeric'
                        });
                    } else if (element.classList.contains('time-only')) {
                        formattedDate = date.toLocaleTimeString('ru-RU', {
                            hour: '2-digit',
                            minute: '2-digit'
                        });
                    } else {
                        formattedDate = date.toLocaleString('ru-RU', {
                            day: '2-digit',
                            month: 'long',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                        });
                    }

                    element.textContent = formattedDate;
                    element.title = 'Нажмите для подробной информации';

                    // Добавляем обработчик клика для показа полной даты
                    element.addEventListener('click', function() {
                        const fullDate = date.toLocaleString('ru-RU', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                        });
                        alert(`Полная дата и время: ${fullDate}`);
                    });
                }
            } catch (e) {
                console.log('Ошибка форматирования даты:', e);
            }
        }
    });
}

function highlightActiveNav() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && href !== '/' && currentPath.startsWith(href)) {
            link.classList.add('active');
            link.classList.add('fw-bold');
        }

        // Особый случай для главной страницы
        if (href === '/' && currentPath === '/') {
            link.classList.add('active');
            link.classList.add('fw-bold');
        }
    });
}

function addAnimations() {
    // Добавляем анимации к карточкам
    const cards = document.querySelectorAll('.card, .list-group-item');
    cards.forEach((card, index) => {
        card.classList.add('fade-in');
        card.style.animationDelay = `${index * 0.1}s`;
    });
}

function initTooltips() {
    // Инициализация Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0 && typeof bootstrap !== 'undefined') {
        tooltipTriggerList.forEach(tooltipTriggerEl => {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

function updateStatusColors() {
    // Обновляем цвета статусов на основе их значений
    const statusElements = document.querySelectorAll('.status-text');

    statusElements.forEach(element => {
        const status = element.textContent.toLowerCase().trim();
        let colorClass = '';

        switch(status) {
            case 'active':
            case 'активный':
            case 'в работе':
                colorClass = 'text-success fw-bold';
                break;
            case 'completed':
            case 'завершен':
            case 'выполнено':
                colorClass = 'text-primary fw-bold';
                break;
            case 'inactive':
            case 'неактивный':
            case 'приостановлен':
                colorClass = 'text-secondary';
                break;
            case 'todo':
            case 'к выполнению':
                colorClass = 'text-warning';
                break;
            case 'in_progress':
            case 'в процессе':
                colorClass = 'text-info fw-bold';
                break;
        }

        if (colorClass) {
            element.className += ' ' + colorClass;
        }
    });
}

// Функция для обновления статистики (можно расширить для AJAX)
function refreshStats() {
    console.log('Обновление статистики...');
    // Здесь можно добавить AJAX запрос для обновления статистики
}

// Экспортируем функции для использования в консоли разработчика
window.TaskTracker = {
    formatDates,
    highlightActiveNav,
    refreshStats
};