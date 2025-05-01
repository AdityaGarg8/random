const { app, BrowserWindow } = require('electron');

let mainWindow;

process.stderr.write = () => {};
app.commandLine.appendSwitch('disable-logging');
app.commandLine.appendSwitch('ignore-certificate-errors');
app.on('ready', () => {
  const url = process.argv[2];

  if (!url) {
    console.error('No URL provided.');
    app.quit();
    return;
  }

  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: false,
    },
  });

  mainWindow.loadURL(url);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
});

app.on('window-all-closed', () => {
  app.quit();
});
