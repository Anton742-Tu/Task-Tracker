document.addEventListener('DOMContentLoaded', function() {
    // Находим блок с userlinks
    const userlinks = document.querySelector('#user-tools');

    if (userlinks) {
        // Создаем ссылку на сайт
        const siteLink = document.createElement('a');
        siteLink.href = '/';
        siteLink.title = 'Перейти на основную часть сайта';
        siteLink.textContent = '🌐 На сайт';
        siteLink.style.cssText = 'color: #4CAF50; font-weight: bold; margin-right: 10px;';

        // Вставляем перед первой ссылкой
        userlinks.insertBefore(siteLink, userlinks.firstChild);

        // Добавляем разделитель
        const separator = document.createTextNode(' / ');
        userlinks.insertBefore(separator, userlinks.children[1]);
    }

    // Также добавляем в заголовок
    const siteName = document.querySelector('#site-name a');
    if (siteName) {
        const headerLink = document.createElement('a');
        headerLink.href = '/';
        headerLink.title = 'Перейти на сайт';
        headerLink.textContent = '🌐';
        headerLink.style.cssText = 'margin-left: 10px; font-size: 0.8em; color: #4CAF50;';

        siteName.parentNode.insertBefore(headerLink, siteName.nextSibling);
    }
});
