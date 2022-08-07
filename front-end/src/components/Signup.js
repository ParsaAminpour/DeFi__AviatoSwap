import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { useState } from 'react'
import "./Signup.css";

export default class Signup extends Component {
    render() {
        return (
            <div id="login-box">
            <div className="left">
                <h1>Sign up</h1>
                
                <input type="text" name="username" placeholder="Username" />
                <input type="text" name="email" placeholder="E-mail" />
                <input type="password" name="password" placeholder="Password" />
                <input type="password" name="password2" placeholder="Retype password" />
                
                <input type="submit" name="signup_submit" value="Sign me up" />
            </div>
            
            </div>
        )
    }
}

