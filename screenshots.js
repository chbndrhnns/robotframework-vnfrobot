var puppeteer = require('puppeteer');

async function shot() {
    const browser = await
    puppeteer.launch();

    const page = await
    browser.newPage();
    await page.goto('https://example.com');

    const inputElement = await
    page.$('p');

    process.stdout.write(await inputElement);

    await inputElement.screenshot({path: 'screenshot.png'});

    await
    browser.close();
}

var a = shot()