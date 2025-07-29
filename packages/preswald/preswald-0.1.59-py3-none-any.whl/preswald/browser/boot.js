/**
 * Boot script for Preswald HTML export
 * This gets appended to index.html during export
 */
async function boot() {
    console.log('[Boot] Starting boot process...');
    // await new Promise(resolve => setTimeout(resolve, 20000));
    const comm = window.__PRESWALD_COMM;

    if (!comm) {
        console.error('[Boot] Error: window.__PRESWALD_COMM is not initialized');
        return;
    }

    console.log('[Boot] PRESWALD_COMM found, proceeding with initialization');

    // Wait until the worker finished Initialising
    await new Promise((resolve) => {
        const unsub = comm.subscribe((msg) => {
            if (msg.type === 'connection_status' && msg.connected) {
                unsub();
                resolve();
            }
        });
    });

    // Fetch the exported project
    const resp = await fetch('project_fs.json');
    const raw = await resp.json();

    // Convert it to the shape loadFilesToFS expects
    const files = {};
    for (const [path, entry] of Object.entries(raw)) {
        if (entry.type === 'text') {
            files[path] = entry.content;
        } else if (entry.type === 'binary') {
            files[path] = Uint8Array.from(atob(entry.content), (c) => c.charCodeAt(0));
        }
    }

    await comm.loadFilesToFS(files);
    console.log('[HTML-export] Project copied into /project');

    const dir_files = await comm.listFilesInDirectory('/project');
    console.log('[HTML-export] Files in /project:', dir_files);

    // Run the entrypoint script
    // await comm.runScript('/project/' + (raw.__entrypoint__ || 'hello.py'));

    console.log('[Client] Running initial script');
    const scriptResult = comm.runScript('/project/' + (raw.__entrypoint__ || 'hello.py'));
    // const scriptResult = await comm.runScript('/project/' + (raw.__entrypoint__ || 'hello.py'));

    // Process any pending updates
    const pendingCount = Object.keys(this.pendingUpdates).length;
    if (pendingCount > 0) {
        console.log(`[Client] Processing ${pendingCount} pending updates`);
        for (const [componentId, value] of Object.entries(this.pendingUpdates)) {
            await this._sendComponentUpdate(componentId, value);
        }
        this.pendingUpdates = {};
    }
}

window.addEventListener('load', boot); 