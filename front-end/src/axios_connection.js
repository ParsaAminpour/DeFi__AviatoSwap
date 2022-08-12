import axios from "axios";

const api_base_url = "http://127.0.0.1:8000/api/";

const axios_connection = axios.create({
    baseURL:api_base_url,
    timeout:5000,
    headers:{
        Authorization: localStorage.getItem("access_token")
        ? `JWT ${localStorage.getItem("access_token")}`
        : null,
        'Content-Type':'application/json',
        accept:'application/json',
    }
})

export default axios_connection;