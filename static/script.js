function upload() {
    let file = document.getElementById("file").files[0];
    if (!file) return;
    let form = new FormData();
    form.append("file", file);
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/uploads");
    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            let percent = (e.loaded / e.total) * 100;
            document.getElementById("progress-bar").style.width = percent + "%";
        }
    };
    xhr.onload = function() {
        document.getElementById("progress-bar").style.width = "0%";
        if (xhr.status === 200) {
            load();
        } else {
            alert("Помилка завантаження: " + xhr.responseText);
        }
    };
    xhr.send(form);
}

function load() {
    fetch("/list").then(r => r.json()).then(data => {
        let s = document.getElementById("search").value.toLowerCase();
        let table = document.getElementById("table");
        table.innerHTML = "";
        
        data.forEach((x, i) => {
            if (!x.name.toLowerCase().includes(s) && !x.type.toLowerCase().includes(s)) return;
            
            let tr = document.createElement("tr");
            let adminButtons = "";
            
            // Показуємо кнопки редагування/видалення лише адміну
            if (USER_ROLE === "admin") {
                adminButtons = `
                    <button class="edit" onclick="edit(${i})">Edit</button>
                    <button class="delete" onclick="del(${i})">Delete</button>
                `;
            }

            tr.innerHTML = `
                <td>${x.name}</td>
                <td>${x.type}</td>
                <td>${x.arch}</td>
                <td>${x.bits}</td>
                <td>${(x.size / 1024 / 1024 / 1024).toFixed(2)} GB</td>
                <td>
                    ${adminButtons}
                    <button onclick="download('${x.file}')">Download</button>
                </td>
            `;
            table.appendChild(tr);
        });
    });

    updateDiskChart();
}

let diskChartInstance = null;
function updateDiskChart() {
    fetch("/disk").then(r => r.json()).then(d => {
        let ctx = document.getElementById("diskChart").getContext("2d");
        if (diskChartInstance) diskChartInstance.destroy();
        
        diskChartInstance = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: ["Зайнято", "Вільно"],
                datasets: [{
                    data: [d.used, d.free],
                    backgroundColor: ["#ff5252", "#3ddc84"],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom', labels: { color: 'white' } } }
            }
        });
    });
}

function edit(i) {
    let name = prompt("Введіть нову назву:");
    if (!name) return;
    let f = new FormData();
    f.append("index", i);
    f.append("name", name);
    fetch("/rename", { method: "POST", body: f }).then(() => load());
}

function del(i) {
    if (!confirm("Видалити цей файл?")) return;
    let f = new FormData();
    f.append("index", i);
    fetch("/delete", { method: "POST", body: f }).then(() => load());
}

function download(filename) {
    window.location = "/download/" + filename;
}

document.getElementById("search").addEventListener("input", load);
load();