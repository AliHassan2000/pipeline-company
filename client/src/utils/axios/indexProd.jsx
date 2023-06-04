import React, { useEffect } from "react";
import { useHistory } from "react-router-dom";
import { createBrowserHistory } from "history";
import axios from "axios";
import { getDataFromLocalStorage } from "../encrypt";

// export const baseUrl = "https://localhost:5000"; //! local
export const baseUrl = "https://10.73.211.88:5000"; //! production
const instance = axios.create();
instance.interceptors.request.use((config) => {
  // const token = localStorage.getItem("cisco_mobily_token");
  const token = getDataFromLocalStorage("cisco_mobily_token_encrypted");
  // console.log("token => " + token);
  if (token) {
    // config.headers["Access-Control-Allow-Origin"] = "*";
    config.headers["X-Auth-Key"] = token;
    config.headers["X-Content-Type-Options"] = "nosniff";
  }
  return config;
});

// Response interceptor for API calls
instance.interceptors.response.use(
  (response) => {
    return response;
  },
  async function (error) {
    // console.clear();
    // console.log(error?.response?.status);
    if (error?.response?.status === 401) {
      // localStorage.removeItem("cisco_mobily_token");
      localStorage.removeItem("cisco_mobily_token_encrypted");
      localStorage.removeItem("module");
      localStorage.removeItem("user");
      createBrowserHistory().push("/");
      window.location.reload();
    } else {
      return error;
    }
  }
);

//https://thedutchlab.com/blog/using-axios-interceptors-for-refreshing-your-api-token

export default instance;
