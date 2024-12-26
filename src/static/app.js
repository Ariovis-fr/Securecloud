
function uploadFile() {
    const fileInput = document.getElementById('fileInput');

    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];

        const formData = new FormData();
        formData.append('file', file);
        fetch('/upload', {
            method: 'POST',
            body: formData
        }).then(response => {
            if (response.ok) {
                display_file();
                fileInput.value = '';
                Toastify({
                    text: "Fichier téléchargé avec succès.",
                    duration: 3000, // 3 seconds
                    gravity: "top", // `top` or `bottom`
                    position: "right", // `left`, `center` or `right`
                    stopOnFocus: true, // Prevents dismissing of toast on hover
                    backgroundColor: "green",
                }).showToast();
            } else {
                Toastify({
                    text: "Erreur lors du téléchargement du fichier.",
                    duration: 3000, // 3 seconds
                    gravity: "top", // `top` or `bottom`
                    position: "right", // `left`, `center` or `right`
                    stopOnFocus: true, // Prevents dismissing of toast on hover
                    backgroundColor: "red",
                }).showToast();
            }
        });
    } else {
        Toastify({
            text: "Veuillez sélectionner un fichier à télécharger.",
            duration: 3000, // 3 seconds
            gravity: "top", // `top` or `bottom`
            position: "right", // `left`, `center` or `right`
            stopOnFocus: true, // Prevents dismissing of toast on hover
            backgroundColor: "red",
        }).showToast();
    }
}

function delete_file(file_id, listItem) {
    fetch(`/delete/${file_id}`, {method: 'DELETE'}).then(response => response.json()).then(data => {
        if (data.message) {
            // If deletion is successful, remove the list item from the DOM
            listItem.remove();
            display_file()
            Toastify({
                text: "Fichier supprimé avec succès.",
                duration: 3000, // 3 seconds
                gravity: "top", // `top` or `bottom`
                position: "right", // `left`, `center` or `right`
                stopOnFocus: true, // Prevents dismissing of toast on hover
                backgroundColor: "green",
            }).showToast();
        } else {
            Toastify({
                text: "Erreur lors de la suppression du fichier.",
                duration: 3000, // 3 seconds
                gravity: "top", // `top` or `bottom`
                position: "right", // `left`, `center` or `right`
                stopOnFocus: true, // Prevents dismissing of toast on hover
                backgroundColor: "red",
            }).showToast();
        }
    })
    .catch(error => {
        Toastify({
            text: "Erreur lors de la suppression du fichier.",
            duration: 3000, // 3 seconds
            gravity: "top", // `top` or `bottom`
            position: "right", // `left`, `center` or `right`
            stopOnFocus: true, // Prevents dismissing of toast on hover
            backgroundColor: "red",
        }).showToast();
    });
}

function display_file() {
    fetch("/get_files")
        .then(response => {
            if (!response.ok) {
                throw new Error(response.statusText);
            }
            return response.json();
        })
        .then(data => {
            const fileList = document.getElementById("file-list");
            fileList.innerHTML = "";
            
            data.forEach(file => {
                if (!document.getElementById(file.id)) {
                    const listItem = document.createElement('li');
                    listItem.classList.add('file-item');
            
                    const linkItem = document.createElement("a");
                    linkItem.href = file.url;
                    linkItem.id = file.id;
                    linkItem.classList.add('file-link');
            
                    // Make the entire list item clickable
                    listItem.appendChild(linkItem);
                    
                    const icon = document.createElement('i');
                    icon.className = "fa-solid fa-file";
                    linkItem.appendChild(icon);
            
                    const textNode = document.createTextNode(file.name);
                    linkItem.appendChild(textNode);
            
                    const deleteButton = document.createElement('button');
                    deleteButton.classList.add('delete-btn');
                    deleteButton.innerHTML = '<i class="fa-solid fa-trash"></i> Delete';
                    deleteButton.onclick = function(event) {
                        event.stopPropagation(); // Prevent clicking delete from triggering the link
                        delete_file(file.id, listItem);
                    };
            
                    listItem.appendChild(deleteButton);
            
                    fileList.appendChild(listItem);
                }
            });
        })
        .catch(error => {
            const fileList = document.getElementById("file-list");
            fileList.innerHTML = `<li style="color: red;">Error fetching data: ${error}</li>`;
        });
}

window.onload = display_file;