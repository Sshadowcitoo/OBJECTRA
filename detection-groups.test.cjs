// detection-groups.test.cjs
const { JSDOM } = require('jsdom');

describe('initDetectionGroups', () => {
    let initDetectionGroups;

    beforeEach(async () => {
        const dom = new JSDOM(`
            <div id="detection-groups-container">
                <div class="group-header">Header</div>
                <div class="group-content hidden">Content</div>
            </div>
        `);
        global.document = dom.window.document;
        global.window = dom.window;

        const module = await import('./static/js/detection-groups.js');
        initDetectionGroups = module.initDetectionGroups;
    });

    test('debería alternar las clases hidden y collapsed al hacer clic', () => {
        initDetectionGroups();
        const header = document.querySelector('.group-header');
        const content = document.querySelector('.group-content');

        header.click();

        expect(content.classList.contains('hidden')).toBe(false);
        expect(header.classList.contains('collapsed')).toBe(true);
    });
});