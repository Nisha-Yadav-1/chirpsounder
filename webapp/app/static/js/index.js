

function hide() {
  document.getElementById("loader").style.display = 'none'; 
}


function displayMessage(folder_name) {
  // alert(folder_name)
  var transmitter_id = document.getElementById("transmitter_id").value;
  // alert(transmitter_id)
  // var folder_name = document.getElementById("foldername").value;
  var url = `http://127.0.0.1:8000/api/filter-ionograms/${folder_name}/${transmitter_id}`;
  var redirect_url = `http://127.0.0.1:8000/filter-ionograms/${folder_name}/${transmitter_id}`;

  const xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById("loader").style.display = "none";
      window.location.href = redirect_url;
    }
  }

xhttp.open("GET", url, true);
xhttp.send();

document.getElementById("loader").innerHTML = `<div class="sr-only text-center card text-primary" style="font-size: 30px;">Once the data has been filtered, you will be automatically redirected to the filtered ionograms page...
<div><span class="spinner-border text-primary" role="status"></div></span>`; 
}
