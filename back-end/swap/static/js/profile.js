let $ = document
let github = $.getElementById('github')
let discord = $.getElementById('discord')
let youtube = $.getElementById('youtube')
let metamask = $.getElementById('meta')


async function CheckConnection() {
    const accounts = await ethereum.request({ method : 'eth_accounts'});
    let result = accounts.length
    return result;
}


window.onload = async() => {
    if(localStorage.getItem('address_status') != null) {
        metamask.classList.remove('disconnect-metamask')
        metamask.classList.add('connect-metamask')  
        metamask.textContent = `Connected(${
                localStorage.getItem('address').trim().slice(1,5)
            }...)`
    }   

    let result_;
    let response = await CheckConnection()
    result_ = response

    if (result_ === 0) {
        localStorage.clear()
        if (Boolean(metamask.className === 'connect-metamask')){
            metamask.classList.toggle('disconnect-metamask') 
            metamask.textContent = 'Connect Wallet'
        }
    
    } else if(result_ === 1) {
        if (Boolean(metamask.className === 'disconnect-metamask')){
            metamask.classList.toggle('connect-metamask') 
            metamask.textContent = `Connected(${
                localStorage.getItem('address').trim().slice(1,5)
            }...)`
        }
    }
}



function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


async function hasAddress() {
    const user_id = await JSON.parse($.getElementById('user_id').textContent);
    let response = await fetch(`http://127.0.0.1:8000/api/wallet/${user_id}/`)
    let data = await response.json();
    if(response.status == 404) {
        return false;
    } else if(response.status == 200) {
        return true
    }
} 

async function addAddress(address, balance, is_zero) {
    const user_id = await JSON.parse($.getElementById('user_id').textContent);
    const csrftoken = getCookie('csrftoken');
    let response = await fetch('http://127.0.0.1:8000/api/wallet/add/', {
        method : 'POST',
        headers : {
            'X-CSRFToken' : csrftoken,
            'Content-type' : 'application/json'
        },
        body:JSON.stringify({
            "address": address,
            "balance": balance,
            "is_zero_address": is_zero
        })
    })
}

metamask.addEventListener('click', async() => {
    let accounts = await ethereum.enable()
    localStorage.setItem('address',ethereum.selectedAddress)
    ethereum.selectedAddress ? localStorage.setItem('address_status', ethereum.selectedAddress) : localStorage.setItem('address_status', null) 
    metamask.classList.remove('disconnect-metamask') 
    metamask.classList.add('connect-metamask')
    metamask.textContent = await `Connected(${
                localStorage.getItem('address').trim().slice(1,5)
            }...)`
    
    let final = prompt('This is your main address (y/n)?')
    final.toLowerCase();    

    if(final == 'y') {
        let has = await hasAddress()
        if (has) {
            // under the creation
            console.log(true)
        } else {
            // under the creation
            console.log(false)
        }
    }
})

