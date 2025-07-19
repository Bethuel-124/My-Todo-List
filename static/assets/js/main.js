
document.addEventListener("DOMContentLoaded", function () {
    
    
    //______________________DBLE_CLICK________________________________________________________________
    document.getElementById("dble_click").addEventListener("dblclick", function () {
        const confir = confirm("Voulez-vous MODIFIER votre profil ?");
        if( confir == true){
            const compte_nom01 = document.getElementById("compte_nom01");
            compte_nom01.innerHTML = "";
            const compte_photo01 = document.getElementById("compte_photo01");
            const compte_photo02 = document.getElementById("compte_photo02");

            const child01 = compte_photo01.children;
            for (i = 0; i< child01.length; i++){
                child01[i].classList.add('d-none');
            };
            compte_photo02.id = "";
            const child02 = compte_nom01.children;
            for (i = 0; i< child02.length; i++){
                child02[i].classList.add('d-none');
            };
            const compte_nom02 = document.createElement('input');
            compte_nom02.id = "compte_nom02"
            compte_nom02.type = "text";
            compte_nom02.style.width = '125px';
            
            const pseudo = document.createElement('input');
            pseudo.type = "button";
            pseudo.id = "pseud";
            pseudo.classList.add("btn");
            pseudo.classList.add("btn-secondary");
            pseudo.style.width = '29px';
            pseudo.style.height = '29px';
            

            const compte_photo03 = document.createElement('input');
            compte_photo03.id = "compte_photo02";
            compte_photo03.type = "file";
            compte_photo03.placeholder = "Photo";
            compte_photo03.classList.add('circle');
            compte_photo03.classList.add('bg-dark');
            
            // Remplacer d-none par d-block
            compte_nom01.appendChild(compte_nom02)
            compte_nom01.appendChild(pseudo)
            
            compte_photo01.appendChild(compte_photo03)

            pseudo.addEventListener('click', change);
            
        } else{
            
        }
        //________________________________________________________________________________________________
            
        async function change(){
            
            const compte_nom01 = document.getElementById("compte_nom01")
            const compte_nom02 = document.getElementById("compte_nom02")
            const compte_photo01 = document.getElementById("compte_photo01")
            const compte_photo03 = document.getElementById("compte_photo02")
            
                try{
                    const formData = new FormData();
                    formData.append("compte_nom", compte_nom02.value);
                    formData.append("compte_photo", compte_photo03.files[0]); // fichierImage = un objet File (input type="file")
                    
                    const token = localStorage.getItem("auth_token");  // ou sessionStorage
                    const response = await fetch("/profile" , {
                        method: "POST",
                        headers: {
                            "Authorization": `Bearer ${token}`
                        },
                        body:formData
                    })
                    
                    const data = await response.json()
                    
                    const img = document.createElement("img");
                    img.style.width = "100px"
                    img.style.height = "100px"
                    img.src = data.photo
                    img.alt = "Photo"
                    img.id = "photo_profile"
                    
                    pseudo.classList.add("d-none")
                    compte_nom02.classList.add("d-none")
                    compte_photo03.classList.add("d-none")
                    compte_photo01.appendChild(img)
                    compte_nom01.innerHTML = data.nom
                }
                
                catch (err) {
                    alert("Erreur : " + err.message);
                }
            }
            
            
        });
        
        
        //______________________ONE_CLICK________________________________________________________________
        
    const pseudo = document.getElementById("pseudo")
    const change = pseudo.addEventListener("click", async function change(){
        
        const compte_nom01 = document.getElementById("compte_nom01")
        const compte_nom02 = document.getElementById("compte_nom02")
        const compte_photo01 = document.getElementById("compte_photo01")
        const compte_photo02 = document.getElementById("compte_photo02")
                
        try{
            const formData = new FormData();
            formData.append("compte_nom", compte_nom02.value);
            formData.append("compte_photo", compte_photo02.files[0]); // fichierImage = un objet File (input type="file")
            const token = localStorage.getItem("auth_token");  // ou sessionStorage
            const response = await fetch("/profile" , {
                method: "POST",
                headers: {
                            "Authorization": `Bearer ${token}`
                        },
                        body:formData
                    })
            
            const data = await response.json()
            
            const img = document.createElement("img");
            img.style.width = "100px"
            img.style.height = "100px"
            img.src = data.photo
            img.alt = "Photo"
            
            pseudo.classList.add("d-none")
            compte_nom02.classList.add("d-none")
            compte_photo02.classList.add("d-none")
            compte_photo01.appendChild(img)
            compte_nom01.innerHTML = data.nom
        }
        
        catch (err) {
                alert("Erreur : " + err.message);
            }
        })


    const tables = document.querySelectorAll('table.table-danger');


        
        
        //________________________________Gérer le clic sur le bouton toggle_____________________________


        
    tables.forEach(function (table, j) {
        const select = table.querySelector('select.vars');
        if (!select) return;

        select.addEventListener('change', function () {
            const value = select.value;
            const tbody = table.querySelector("tbody");
            const rows = tbody.querySelectorAll("tr");
            
            if (value === "confirmer") {
                rows.forEach(row => {
                    row.querySelectorAll("input").forEach(input => input.disabled = true);
                });
            } else if (value === "modifier") {
                rows.forEach(row => {
                    row.querySelectorAll("input").forEach(input => input.disabled = false);
                });
            } else if (value === "supprimer") {
                
                const feedbackTable = document.querySelectorAll("table.table-success")[j];
                const feedbackRow = feedbackTable?.rows[1];

                if (feedbackRow) {
                    feedbackRow.cells[0].innerHTML = "";
                    feedbackRow.cells[1].innerHTML = "";
                    feedbackRow.cells[2].innerHTML = "";
                }
                rows.forEach(row => {
                    row.querySelectorAll("input").forEach(input => input.value = "");
                });
            } else if (value === "plus") {
                const lastRow = rows[rows.length - 1];
                const newRow = lastRow.cloneNode(true);
                newRow.querySelectorAll("input").forEach(input => {
                    input.value = "";
                    input.disabled = false;
                });
                tbody.appendChild(newRow);
            } else if (value === "moin") {
                if (rows.length > 1) tbody.deleteRow(rows.length - 1);
            }

            select.selectedIndex = 0;
        });
        
        // ____________________ Gérer le clic sur le bouton toggle ____________________
        const toggle = table.parentElement.querySelector(".toggle.ms-auto");
        
        toggle.addEventListener("click", async function () {
            alert(" requette en cour")
            
            const rows = table.querySelectorAll("tbody tr");
                        const tableau = [];

                        rows.forEach((row, i) => {
                            tableau.push({
                                id: i,
                                horaire: row.cells[1].querySelector("input")?.value || "",
                                tache: row.cells[2].querySelector("input")?.value || "",
                                statut: row.cells[3].querySelector("input")?.value || ""
                            });
                        });

                        try {
                            const response = await fetch("/programme", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({ tableau: tableau, identifiant: j })
                            });

                            if (!response.ok) {
                                const text = await response.text();
                                throw new Error(`Erreur serveur : ${response.status} - ${text}`);
                            }

                            const data = await response.json();
                            const { message01, message02, message03 } = data;

                            const feedbackTable = document.querySelectorAll("table.table-success")[j];
                            const feedbackRow = feedbackTable?.rows[1];

                            if (feedbackRow) {
                                feedbackRow.cells[0].innerHTML = message01;
                                feedbackRow.cells[1].innerHTML = message02;
                                feedbackRow.cells[2].innerHTML = message03;
                            }
                        } catch (err) {
                            alert("Erreur : " + err.message);
                        }
                    });
                });
            });
