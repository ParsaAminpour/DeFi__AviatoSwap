import React from "react";
import "./Home.css";
import right_wallpaper5 from "./images/right_wallpaper5.jpg"
import axios from "axios";
import { Link } from "react-router-dom";

class Home extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            'address' : this.props.address,
            'balance' : this.props.balance,
            'wallet_status' : this.props.wallet_status
        }
    }

    render() {
        return(
            <React.Fragment>
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


        </React.Fragment>
        )
    }
}

export default Home;

