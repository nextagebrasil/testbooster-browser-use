docker build -t testbooster-browser-use .
docker run --rm -p 9090:9090 --env-file .env testbooster-browser-use

Quando executo no docker pode dar erro na hora de instanciar o browser, erro: "║ Looks like you launched a headed browser without having a XServer running. ║ ║ Set either 'headless: true' or use 'xvfb-run <your-playwright-app>' before running Playwright. ║ ║  ║ ║ <3 Playwright Team   "
Para resolver fui no arquivo: "B:\WorkSpaceTestBooster\testbooster-browser-use\browser_use\browser\browser.py", linha: headless: bool = True (adicionei o valor de True, como false não funciona)

