import {React, useState} from "react";
import "./Home.css";
import { ethers } from "ethers";
import right_wallpaper5 from "./images/right_wallpaper5.jpg"
import axios from "axios";
import { MetaMaskProvider } from "metamask-react"
import { Link } from "react-router-dom";

const Home = () => {
    const [address_state, setAddress] = useState(null);
    const [balance_state, setBalance] = useState(null);
    const [status_state, setStatus] = useState(false);
    const provider = new ethers.providers.Web3Provider(
        window.ethereum
    )

    window.addEventListener('load' , () => {
        if(window.ethereum.selectedAddress == null) {
            console.log("reload listener executed")
            localStorage.removeItem("address");
            localStorage.removeItem("balance");
            localStorage.removeItem("status")

            setAddress(null)
            setBalance(null)
            setStatus(false)
            document.getElementById("connect_btn").style.background = "#ff7e7e";
            document.getAnimations("connect_btn").innerHTML = "Connect Wallet"
        } else {
            document.getElementById("connect_btn").style.background = "#a1ffb5";
            document.getElementById("connect_btn").innerHTML = "Wallet Connected"
        }
    })

    window.ethereum.on("accountsChanged", async() => {
        console.log("account changes listener executed");
        window.location.reload();
    })

    const connect_wallet = async() => {
        console.log("connect_wallet executed")
        const account = await window.ethereum.request({
            method : 'eth_requestAccounts'
        })

        changeHandler(account[0]);
    }


    const changeHandler = async(account) => {
        console.log("changeHandler_function")
        const balance = await provider.getBalance(account);
        const main_balance = ethers.utils.formatEther(balance)

        localStorage.setItem("address", window.ethereum.selectedAddress);
        localStorage.setItem("balance",Math.floor(main_balance*1000)/1000);
        localStorage.setItem("status", true)
        
        setAddress(account);
        setBalance(Math.floor(main_balance*1000)/1000);
        setStatus(true);

        window.location.reload();
    }

    return(
    <div>
        <div className="section-left">

            <div className="logo-div">
                <h1 className="logo"> Aviato Swap </h1>
            </div>

            <div id="buttons">
                <button className="home">
                    <Link className='button_link' to="https://github.com/ParsaAminpour/Aviato-Swap"> Source </Link></button>

                <button className="chatroom"> 
                    <Link className='button_link' to="/chatroom/">
                        Chatroom </Link>
                </button>

                <button className="profile">
                    <Link className='button_link' to="/profile/"> Profile </Link> 
                </button>

                <button className="signup"> <Link className='button_link' to="/signup/"> SignUp </Link> 
                </button>

                <button className="login"> <Link className='button_link' to="/login/"> Login </Link>
                </button>

                <button id="connect_btn" className="connect-wallet" onClick={connect_wallet}> Connect Wallet </button>
                

            </div>

            <div className="explain-content">
                <h1 className="explain-text">
                    Swap, Trading on a powerful platform in full <br /> 
                    Decentralize <br />
                    upon Goerli Test network
                </h1>
            </div>

            <div className="button">
                <button className="my-button">Swap</button>    
            </div>                
        </div>

        <div className="section-right">
            <img src={right_wallpaper5} className="right-wallpaper" alt="right-wallpaper" />
        </div>

        <div className="wallet-info">
            <h2> address: {localStorage.getItem("address")}</h2> <br />
            <h2> balance: {localStorage.getItem("balance")}</h2>
        </div>
           
    </div>
    )
}

export default Home;

