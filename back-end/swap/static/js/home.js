import MetaMaskOnboarding from '@metamask/onboarding';
const boarding = new MetaMaskOnboarding() 
let $ = document
let metamask = $.getElementById('.metamask')
let address = $.getElementById('address')

const checkMetaMaskInstalled = () => {
    const { ethereum } = window;
    return Boolean(ethereum && ethereum.isMetaMask)
}

const onclickInstallMetaMask = () => {
    boarding.startOnboarding();
}

async function ConnectingWallet() {
    return await ethereum.request({method : 'eth_accounts'})
}

let connectedWalletShowing = (accounts) => {
    metamask.classList.toggle('connect-metamask')
    metamask.innerHTML = 'Connected'
    address.innerHTML = `${accounts[0].slice(0,6)}...`
}

const ModifingForMetaMaskStatus = () => {
    if (!checkMetaMaskInstalled()) {
        metamask.classList.remove('connect-metamask')
        metamask.classList.add('disconnect-metamask')
        metamask.innerHTML = 'Install Metamask'
        metamask.addEventListener('click', onclickInstallMetaMask)
    } 
    else {
        ConnectingWallet().then((accounts) => {
            if (accounts && accounts[0] >= 0){
                connectedWalletShowing(accounts)
            } else {
                metamask.innerHTML = 'Connect the wallet'
            }
        })
    }
}
metamask.addEventListener('click' , async() => {
    
})
ModifingForMetaMaskStatus();