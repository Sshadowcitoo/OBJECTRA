// detection-groups.js

export function initDetectionGroups(containerSelector = '#detection-groups-container') {
    const container = document.querySelector(containerSelector);
    if (!container) return;

    container.addEventListener('click', (event) => {
        const groupHeader = event.target.closest('.group-header');
        if (!groupHeader) return;

        const groupContent = groupHeader.nextElementSibling;
        if (groupContent && groupContent.classList.contains('group-content')) {
            groupContent.classList.toggle('hidden');
            groupHeader.classList.toggle('collapsed');
        }
    });
}