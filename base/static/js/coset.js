function generateDesktopNav() {
    const nav = document.getElementById('desktop-nav');
    Object.keys(menuData).forEach(key => {
        const item = menuData[key];
        const button = document.createElement('button');
        button.className = 'flex-1 px-6 py-4 font-medium transition duration-300 hover:bg-deep-blue';
        button.textContent = item.title;
        button.onclick = () => toggleMegaMenu(key);
        nav.appendChild(button);
    });
}

// Generate desktop megamenus
function generateDesktopMegamenus() {
    const container = document.getElementById('megamenu-container');
    Object.keys(menuData).forEach(key => {
        const item = menuData[key];
        const megamenu = document.createElement('div');
        megamenu.id = `megamenu-${key}`;
        megamenu.className = 'overflow-hidden max-h-0 bg-white/95 z-100 md:block absolute w-full';
        
        const inner = document.createElement('div');
        inner.className = 'max-w-7xl mx-auto px-8 py-8';
        
        const grid = document.createElement('div');
        grid.className = 'grid grid-cols-3 gap-8';
        
        item.sections.forEach(section => {
            const col = document.createElement('div');
            const title = document.createElement('h3');
            title.className = 'font-semibold text-deep-blue mb-4 text-lg';
            title.textContent = section.title;
            col.appendChild(title);
            
            const ul = document.createElement('ul');
            ul.className = 'space-y-2';
            section.links.forEach(link => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = link.href;
                a.className = 'text-gray-800 hover:text-maroon';
                a.textContent = link.text;
                li.appendChild(a);
                ul.appendChild(li);
            });
            col.appendChild(ul);
            grid.appendChild(col);
        });
        
        inner.appendChild(grid);
        megamenu.appendChild(inner);
        container.appendChild(megamenu);
    });
}

// Generate mobile navigation
function generateMobileNav() {
    const nav = document.getElementById('mobile-nav');
    Object.keys(menuData).forEach(key => {
        const item = menuData[key];
        
        const button = document.createElement('button');
        button.className = 'w-full text-left px-4 py-3 text-white hover:coset-gray1 rounded';
        button.textContent = item.title;
        button.onclick = () => toggleMobileMegaMenu(key);
        nav.appendChild(button);
        
        const submenu = document.createElement('div');
        submenu.id = `mobile-megamenu-${key}`;
        submenu.className = 'overflow-hidden max-h-0 transition-all duration-300 ease-in-out bg-coset-gray3 ml-4';
        
        const inner = document.createElement('div');
        inner.className = 'py-2';
        
        item.sections.forEach(section => {
            const sectionDiv = document.createElement('div');
            sectionDiv.className = 'mb-4';
            
            const title = document.createElement('h4');
            title.className = 'font-semibold text-white px-4 py-2';
            title.textContent = section.title;
            sectionDiv.appendChild(title);
            
            section.links.forEach(link => {
                const a = document.createElement('a');
                a.href = link.href;
                a.className = 'block px-6 py-2 text-gray-200 hover:bg-maroon';
                a.textContent = link.text;
                sectionDiv.appendChild(a);
            });
            
            inner.appendChild(sectionDiv);
        });
        
        submenu.appendChild(inner);
        nav.appendChild(submenu);
    });
}

// Initialize menus on page load
document.addEventListener('DOMContentLoaded', () => {
    generateDesktopNav();
    generateDesktopMegamenus();
    generateMobileNav();
});

let currentMenu = null;
let currentMobileMenu = null;

function toggleMegaMenu(menuId) {
    const menu = document.getElementById('megamenu-' + menuId);
    
    if (currentMenu && currentMenu !== menu) {
        currentMenu.classList.add('max-h-0');
        currentMenu.classList.remove('max-h-[500px]');
    }
    
    if (menu.classList.contains('max-h-0')) {
        menu.classList.remove('max-h-0');
        menu.classList.add('max-h-[500px]');
        currentMenu = menu;
    } else {
        menu.classList.add('max-h-0');
        menu.classList.remove('max-h-[500px]');
        currentMenu = null;
    }
}

function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    const hamburger = document.querySelector('.hamburger');
    const spans = hamburger.querySelectorAll('span');
    
    if (menu.classList.contains('max-h-0')) {
        menu.classList.remove('max-h-0');
        menu.classList.add('max-h-[2000px]');
        spans[0].style.transform = 'rotate(-45deg) translate(-5px, 6px)';
        spans[1].style.opacity = '0';
        spans[2].style.transform = 'rotate(45deg) translate(-5px, -6px)';
    } else {
        menu.classList.add('max-h-0');
        menu.classList.remove('max-h-[2000px]');
        spans[0].style.transform = '';
        spans[1].style.opacity = '';
        spans[2].style.transform = '';
        
        document.querySelectorAll('[id^="mobile-megamenu-"]').forEach(submenu => {
            submenu.classList.add('max-h-0');
            submenu.classList.remove('max-h-[2000px]');
        });
    }
}

function toggleMobileMegaMenu(menuId) {
    const menu = document.getElementById('mobile-megamenu-' + menuId);
    
    if (currentMobileMenu && currentMobileMenu !== menu) {
        currentMobileMenu.classList.add('max-h-0');
        currentMobileMenu.classList.remove('max-h-[2000px]');
    }
    
    if (menu.classList.contains('max-h-0')) {
        menu.classList.remove('max-h-0');
        menu.classList.add('max-h-[2000px]');
        currentMobileMenu = menu;
    } else {
        menu.classList.add('max-h-0');
        menu.classList.remove('max-h-[2000px]');
        currentMobileMenu = null;
    }
}

document.addEventListener('click', function(event) {
    const nav = document.querySelector('nav');
    const menus = document.querySelectorAll('[id^="megamenu-"]');
    const mobileMenu = document.getElementById('mobile-menu');
    const hamburger = document.querySelector('.hamburger');
    
    if (!nav.contains(event.target) && 
    !Array.from(menus).some(menu => menu.contains(event.target)) &&
    !mobileMenu.contains(event.target) &&
    !hamburger.contains(event.target)) {
        menus.forEach(menu => {
            menu.classList.add('max-h-0');
            menu.classList.remove('max-h-[500px]');
        });
        currentMenu = null;
    }
});
// Generate desktop navigation