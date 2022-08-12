import React from "react";
import { ReactDOM } from "react";
import axios from "axios";
import Home from "./components/Home"
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import SignInSide from "./components/Signup";
import Login from "./components/Login";
import Swap from "./components/Swap"

class App extends React.Component {
    render() {
        return(
            <Router>
                <React.StrictMode>
                    <Routes>
                        <Route exact path="/" caseSensitive={false} element={<Home />} />

                        <Route exact path="/signup" caseSensitive={false} element={<SignInSide />} />

                        <Route exact path="/login" caseSensitive={false} element={<Login />} />

                        <Route exact path="/swap" caseSensitive={false} element={<Swap />}/>
                    </Routes>
                </React.StrictMode>
            </Router>
        )
    }
}

export default App;