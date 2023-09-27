import React, { Component, useState, useEffect } from 'react';


function App() {

  const [wallet, setWallet] = useState("0x0");
  
  const connectingToWallet = () => {
    useEffect(() => {
      console.log("Ethereum wallet is connecting...");

      return () => {
        console.log("Component has just been unmounted");
      }
    }, []);

    useEffect(() => {
      console.log("Ethereum wallet address has just been changed");
    }, [wallet])

    if(window.ethereum && wallet === "0x0") {
      setWallet(window.ethereum.enable().then(resolve => setWallet(resolve)))
    }
  }

  return (
    <div>
      <AviatoSwapTitle version_number={2} />
      <SwapSection />
    </div>
  )
}

const AviatoSwapTitle = (props) => {
  return (
    <h1> <center> Aviato Swap { props.version_number } </center></h1>
  )
}

const SwapSection = (props) => {
  return(
    <div className='Swap'>
      <input type="text"></input> <br /><br />
      <button type='submit'> Swap </button>
    </div>
  )
} 

export default App;
