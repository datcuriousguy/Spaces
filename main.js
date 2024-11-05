
// main.js
const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
    const win = new BrowserWindow({
        width: 1000,
        height: 700,
        minWidth: 1000,
        minHeight: 700,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'), // optional
            nodeIntegration: true, // enables using Node.js in the app
        },
    });

    win.loadFile('spaces_main_webpage.html'); // Load your main HTML file here
}

// app.whenReady().then(createWindow);

// app.on('window-all-closed', () => {
//     if (process.platform !== 'darwin') {
//         app.quit();
//     }
// });

// app.on('activate', () => {
//     if (BrowserWindow.getAllWindows().length === 0) {
//         createWindow();
//     }
// });




const { spawn } = require('child_process');

function startPythonServer() {
    const pythonProcess = spawn('python', ['SPACES_api.py']); // Replace 'python' with 'python3' if necessary

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python API: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python API Error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python API exited with code ${code}`);
    });
}

app.whenReady().then(() => {
    startPythonServer(); // Start Python server
    createWindow();       // Then create Electron window
});
