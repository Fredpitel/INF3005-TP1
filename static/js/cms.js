function suggestId(titre){
    var id_value = titre.replace(/[^\w\s]/gi, '').replace(/[\s]/gi, '_').toLowerCase();

    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
            document.getElementById("identifiant").value = xhr.responseText
        } else {
            console.log('Erreur avec le serveur');
        }
      }
    };

    xhr.open("GET", "/suggest_id/" + id_value, true);
    xhr.send();
}

function checkId(id) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
            if (xhr.responseText === "false") {
                document.getElementById("erreur").style.display = "inherit"
            } else {
                document.getElementById("erreur").style.display = "none"
            }
        } else {
            console.log('Erreur avec le serveur');
        }
      }
    };

    xhr.open("GET", "/check_id/" + id, true);
    xhr.send();
}