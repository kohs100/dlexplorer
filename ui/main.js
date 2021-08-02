const regCode = /(RJ|VJ|BJ)\d{6}/g;

function updateInfo(rjcode) {
    const xhr_info = new XMLHttpRequest();
    var sbutton = document.getElementById('buttonSearch');

    var loading = document.getElementById('loadingIcon');
    var loaded = document.getElementById('buttonSearchGo');

    xhr_info.open('GET', 'db/'+rjcode, true);
    xhr_info.responseType = 'json';
    xhr_info.onload = () => {
        var img = document.getElementById('workImage');

        img.src = 'db/'+rjcode+'/img';
        img.onclick = function() {
            location.href = xhr_info.response.req_url;
        }

        document.getElementById('workContent').innerHTML =
        'Title: ' + xhr_info.response.title + '<br>' +
        'Brand: ' + xhr_info.response.maker_name
        
        loading.style.display = 'none';
        loaded.style.display = 'block';
    }
    xhr_info.send();
    loading.style.display = 'inline-block';
    loaded.style.display = 'none';
}

window.onload = function() {
    var sbar = document.getElementById('barSearch');
    var sbutton = document.getElementById('buttonSearch');
    sbutton.onclick = function() {
        res = regCode.exec(sbar.value)
        if(res) {
            sbar.value = res[0];
            updateInfo(res[0])
        }
    }
    sbar.onkeydown = function(e) {
        if (e.code == 'Enter') {
            res = regCode.exec(sbar.value)
            if(res) {
                sbar.value = res[0];
                updateInfo(res[0])
            }
        }
    }
}