let username_input = document.querySelector('.username')
let username_msg = document.getElementById('username-msg')

let email_input = document.querySelector('.email')
let email_msg = document.getElementById('email-msg')

let password1_input = document.querySelector('.password1')
let password1_msg = document.getElementById('password1-msg')

let password2_input = document.querySelector('.password2')
let password2_msg = document.getElementById('password2-msg')


function usernameValidation() {
    var username_status = false;

    if (username_input.value.length < 10) {
        username_msg.style.display = 'block';
        username_msg.style.color = 'red';
        username_msg.innerHTML = 'usenrame should be more than 10 char';                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
    } else {
        username_msg.style.display = 'block';
        username_msg.style.color = 'green';
        username_msg.innerHTML = 'Valid username';
        username_status = true;
    }
}

function emailValidation() {
    var email_status = false;
    email = email_input.value
    const pattern = /^[a-z]+(?:(?:\.[a-z]+)+\d*|(?:_[a-z]+)+(?:\.\d+)?)?@(?!.*\.\.)[^\W_][a-z\d.]+[a-z\d]{2}$/g
    const result = pattern.exec(email)
   
    if(!result) {
        email_msg.style.display = 'block';
        email_msg.style.color = 'red';
        email_msg.innerHTML = 'The email is invalid';
    } else {
        email_msg.style.display = 'block';
        email_msg.style.color = 'green';
        email_msg.innerHTML = 'The email is valid';
        email_status = true;
    }
}

function passwod1Validation() {
    var password1_status = false
    if (password1_input.value.length < 12) {
        password1_msg.style.display = 'block';
        password1_msg.style.color = 'red';
        password1_msg.innerHTML = 'password should be more than 12 char';                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
    } else {
        // password1_msg.style.color = 'green';
        password1_msg.innerHTML = '';
        password1_msg.style.display = 'none';
        password1_status = true;
    }
}

function password2Validation() {
    var password2_status = false;
    if(password1_input.value != password2_input.value) {
        password2_msg.style.display = 'block';
        password2_msg.style.color = 'red';
        password2_msg.style.innerHTML = 'The passwords are NOT same';
    } else {
        password2_msg.style.display = 'block';
        password2_msg.style.color = 'green';
        password2_msg.innerHTML = 'valid password';
        password2_status = true;
    }
}

const url = 'http://127.0.0.1/api/user/add'
async function submit(){
    submit_button = document.querySelector('.submiting')
    const response = await fetch(url)
    const data = await response.json()
    const result = await data.result
}