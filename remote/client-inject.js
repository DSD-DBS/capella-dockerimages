/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

const injectInterval = setInterval(() => {
    if (!client) return;
    client.OPEN_TIMEOUT = 30_000;

    for (const [id, win] of Object.entries(client.id_to_window).toReversed()) {
        if (win.metadata.modal) {
            if (client.topwindow !== parseInt(id)) {
                console.log("Forcing focus on modal window", id);
                client.set_focus(win);
            }
            break;
        }
    }
}, 100);
console.log("Inject script running on interval", injectInterval);
