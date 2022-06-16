let $ = document
let github = $.getElementById('github')
let discord = $.getElementById('discord')
let youtube = $.getElementById('youtube')
let metamask = $.getElementById('meta')
let address = $.getElementById('wallet_addr')


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

window.addEventListener('load', async() => {
    // address.textContent = await ethereum.selectedAddress
    if (typeof web3 !== 'undefined') {
        console.log('Web3 Detected! ' + web3.currentProvider.constructor.name)
        window.web3 = new Web3(web3.currentProvider);
    } else {
        console.log('No Web3 Detected... using HTTP Provider')
        window.web3 = new Web3(new Web3.providers.HttpProvider("https://mainnet.infura.io/v3/30c699ab1b3f408aa64c9a09de9ee015"));
    }


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
f
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
})




async function CheckConnection() {
    const accounts = await ethereum.request({ method : 'eth_accounts'});
    let result = accounts.length
    return result;
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

async function changeAddress(address, balance, is_zero) {
    const user_id = await Json.parse($.getElementById('user_id').textContent)
    const csrftoken = getCookie('csrftoken');
    let fetching = await fetch(`http://127.0.0.1:8000/api/wallet/${user_id}/`, {
        method : 'PUT',
        headers : {
            'X-CSRFToken' : csrftoken,
            'Content-type' : 'application/json'
        },
        body : JSON.stringify({
            'address' : address,
            'balance' : balance,
            'is_zero_address' : is_zero
        })
    })
    let response = fetching.json()
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

async function get_balance(address) {
    try {
        web3.eth.getBalance(address, (error, wei) => {
            if(!error) {
                var balance = web3.fromWei(wei, 'ether')
                return balance
            }
        })
    } catch(err) {
        return false
    }
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

    if(final.toLowerCase() === 'y') {
        let has = await hasAddress()
        let balance = web3.eth.getBalance(ethereum.selectedAddress)
        let is_zero;
        balance === 0 ? is_zero = true : is_zero = false
        if (has) {
            // changeAddress(ethereum.selectedAddress, balance, is_zero)
            alert('true')unserv
        } else {
            // addAddress(ethereum.selectedAddress, balance, is_zero)
            alert('false')
        }
    } else if(final.toLowerCase() == 'n') {
        console.log('returned No')
    }
})

