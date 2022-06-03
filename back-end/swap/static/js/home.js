import MetaMaskOnboarding from '@metamask/onboarding';
const onboarding = new MetaMaskOnboarding() 
let $ = document
let metamask = $.getElementById('metamask')
let status = $.getElementById('address')


metamask.addEventListener('click', () => {
    ethereum.enable().then((accounts) => {
        let account = `${accounts[0].slice(0,6)}...`
        status.innerHTML = account
        metamask.classList.add('connect-metamask')
        metamask.innerHTML = 'Connected'

        // setting localStorage issues
        localStorage.setItem('btn' , 'connected')
        localStorage.setItem('address', account)
        location.reload();
        }) 
})

window.onload = () => {
    if(localStorage.getItem('btn') === 'connected') {
        metamask.classList.add('connect-metamask')
    } else {
        metamask.classList.toggle('disconnect-metamask')
    }
}



// // Check meta has already installed or vise versa
// const isMetaMaskInstalled = () => {
//     const { ethereum } = window;
//     return Boolean(ethereum && ethereum.isMetaMask);
// }


// const onClickInstallMetaMask = () => {
//     onboarding.startOnboarding();
// }


// async function connectWallet() {
//     return await ethereum.request({
//         method: 'eth_accounts'});
// }

// let connected = (accounts) => {
//     metamask.innerHTML = 'Connected'
//     metamask.classList.toggle('connect-metamask')
//     status.innerHTML = accounts[0]
//     status.style.color = 'green';
// }

// metamask.addEventListener('click', async () => {
//     metamask.style.backgroundColor = '#cccccc';

//     try {
//         const accounts = await ethereum.request({method: 'eth_requestAccounts'})
//         connected(accounts)
//     } catch (error) {
//         console.error(error);
//     }
// })

// const MetaMaskClientCheck = () => {
//     if (!isMetaMaskInstalled()) {
//         status.innerText = 'You need to Install a Wallet';
//         metamask.innerText = 'Install MetaMask'
//         metamask.onclick = onClickInstallMetaMask;
//     } else {
//         connectWallet().then((accounts) => {
//             if (accounts && accounts[0] >= 0) {
//                 connected(accounts)
//             } else {
//                 status.innerHTML = 'Connect your wallet'
//                 metamask.classList.toggle('disconnect-metamask')
//                 metamask.innerText = 'Connect MetaMask'
//             }
//         })
//     }
// }

// MetaMaskClientCheck();