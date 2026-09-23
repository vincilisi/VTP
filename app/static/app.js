let ultimoRisultato = null;
const analysisStatus = document.getElementById("analysisStatus");
const connectionStatus = document.getElementById("connectionStatus");
const fileInput = document.getElementById("pdf");
const fileName = document.getElementById("fileName");

/* =========================
   ANALISI STATINO
========================= */

document
.getElementById("analizza")
.addEventListener("click", async () => {

    const file =
        document.getElementById("pdf").files[0];

    if (!file) {

        alert(
            "Seleziona un PDF"
        );

        return;
    }

    analysisStatus.textContent = "Analisi dello statino in corso...";
    analysisStatus.classList.remove("error");

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    const response =
        await fetch(
            "/api/estrai",
            {
                method: "POST",
                body: formData
            }
        );

    const data =
        await response.json();

    if (!response.ok) {
        analysisStatus.textContent = "Non e' stato possibile analizzare il file.";
        analysisStatus.classList.add("error");
        return;
    }

    ultimoRisultato = data;

    const tbody =
        document.getElementById(
            "righe"
        );

    if (tbody) {

        tbody.innerHTML = "";

        data.righe.forEach(
            (riga) => {

                const tr =
                    document.createElement("tr");

                tr.innerHTML = `
                    <td>${riga.giorno}</td>
                    <td>${riga.servizio}</td>
                    <td>${riga.aviaria}</td>
                    <td>${riga.radiogeno}</td>
                `;

                tbody.appendChild(
                    tr
                );
            }
        );
    }

    const ta =
        document.getElementById("ta");

    const tr =
        document.getElementById("tr");

    if (ta) {
        ta.textContent =
            data.totale_aviaria;
    }

    if (tr) {
        tr.textContent =
            data.totale_radiogeno;
    }

    document.getElementById("totaleComplessivo").textContent =
        data.totale_aviaria + data.totale_radiogeno;
    document.getElementById("scaricaPdf").disabled = false;
    analysisStatus.textContent = data.righe.length
        ? `${data.righe.length} turni VTP rilevati. Puoi generare il PDF.`
        : "Nessun turno Venezia Terminal Passeggeri trovato.";
});


/* =========================
   SALVATAGGIO PROFILO
========================= */

const btnSalvaProfilo =
    document.getElementById(
        "salvaProfilo"
    );

if (btnSalvaProfilo) {

    btnSalvaProfilo.addEventListener(
        "click",
        () => {

            const profilo = {

                nome:
                    document.getElementById("nome").value,

                cognome:
                    document.getElementById("cognome").value,

                targa:
                    document.getElementById("targa").value,

                modello:
                    document.getElementById("modello").value
            };

            localStorage.setItem(
                "vtpProfilo",
                JSON.stringify(
                    profilo
                )
            );

            alert(
                "Profilo salvato"
            );
        }
    );
}


/* =========================
   CARICA PROFILO
========================= */

const profiloSalvato =
    localStorage.getItem(
        "vtpProfilo"
    );

if (profiloSalvato) {

    const p =
        JSON.parse(
            profiloSalvato
        );

    if (document.getElementById("nome"))
        document.getElementById("nome").value =
            p.nome || "";

    if (document.getElementById("cognome"))
        document.getElementById("cognome").value =
            p.cognome || "";

    if (document.getElementById("targa"))
        document.getElementById("targa").value =
            p.targa || "";

    if (document.getElementById("modello"))
        document.getElementById("modello").value =
            p.modello || "";
}


/* =========================
   FIRMA
========================= */

const canvas =
    document.getElementById(
        "firma"
    );

if (canvas) {

    const ctx =
        canvas.getContext("2d");

    let disegnando =
        false;

    function getPos(e) {

        const rect =
            canvas.getBoundingClientRect();

        return {

            x: (e.clientX - rect.left) * (canvas.width / rect.width),

            y: (e.clientY - rect.top) * (canvas.height / rect.height)
        };
    }

    canvas.addEventListener(
        "pointerdown",
        (e) => {

            e.preventDefault();
            disegnando = true;

            try {
                canvas.setPointerCapture(e.pointerId);
            } catch (error) {
                // Safari can draw without pointer capture.
            }

            const p =
                getPos(e);

            ctx.beginPath();

            ctx.moveTo(
                p.x,
                p.y
            );
        }
    );

    canvas.addEventListener(
        "pointermove",
        (e) => {

            if (
                !disegnando
            ) {
                return;
            }

            e.preventDefault();

            const p =
                getPos(e);

            ctx.lineWidth = 2;

            ctx.lineCap =
                "round";

            ctx.lineTo(
                p.x,
                p.y
            );

            ctx.stroke();
        }
    );

    function terminaFirma(e) {

        if (!disegnando) {
            return;
        }

        disegnando = false;

        try {
            if (canvas.hasPointerCapture(e.pointerId)) {
                canvas.releasePointerCapture(e.pointerId);
            }
        } catch (error) {
            // Pointer capture is optional for touch drawing.
        }

        salvaFirma();
    }

    canvas.addEventListener("pointerup", terminaFirma, { passive: false });
    canvas.addEventListener("pointercancel", terminaFirma, { passive: false });

    function salvaFirma() {

        const firma =

            canvas.toDataURL(
                "image/png"
            );

        localStorage.setItem(
            "vtpFirma",
            firma
        );
    }

    const firmaSalvata =
        localStorage.getItem(
            "vtpFirma"
        );

    if (firmaSalvata) {

        const img =
            new Image();

        img.onload = () => {

            ctx.drawImage(
                img,
                0,
                0
            );
        };

        img.src =
            firmaSalvata;
    }

    const btnPulisci =
        document.getElementById(
            "pulisciFirma"
        );

    if (btnPulisci) {

        btnPulisci.addEventListener(
            "click",
            () => {

                ctx.clearRect(
                    0,
                    0,
                    canvas.width,
                    canvas.height
                );

                localStorage.removeItem(
                    "vtpFirma"
                );
            }
        );
    }
}


/* =========================
   GENERAZIONE PDF
========================= */

const btnScaricaPdf =
    document.getElementById(
        "scaricaPdf"
    );

if (btnScaricaPdf) {

    btnScaricaPdf.addEventListener(
        "click",
        async () => {

            if (!ultimoRisultato) {
                alert("Analizza prima uno statino PDF");
                return;
            }

            const datiPdf = {
                ...ultimoRisultato,
                nome: document.getElementById("nome").value,
                cognome: document.getElementById("cognome").value,
                targa: document.getElementById("targa").value,
                modello: document.getElementById("modello").value,
                firma: canvas ? canvas.toDataURL("image/png") : ""
            };

            const response = await fetch(
                "/api/genera-pdf",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(datiPdf)
                }
            );

            if (!response.ok) {
                alert("Impossibile generare il PDF");
                return;
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");

            link.href = url;
            link.download = "rimborso.pdf";
            link.click();
            window.URL.revokeObjectURL(url);
        }
    );
}


if (fileInput) {
    fileInput.addEventListener("change", () => {
        const selectedFile = fileInput.files[0];
        fileName.textContent = selectedFile
            ? selectedFile.name
            : "Seleziona lo statino";
    });
}


window.addEventListener("online", () => {
    connectionStatus.textContent = "Pronto";
});

window.addEventListener("offline", () => {
    connectionStatus.textContent = "Offline";
});


let installPrompt;
const installButton = document.getElementById("installaApp");

window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    installPrompt = event;
    installButton.hidden = false;
});

installButton.addEventListener("click", async () => {
    if (!installPrompt) {
        return;
    }

    installPrompt.prompt();
    await installPrompt.userChoice;
    installPrompt = null;
    installButton.hidden = true;
});


if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/service-worker.js");
    });
}