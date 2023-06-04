import React, { useState, createContext } from "react";
import axios, { baseUrl } from "../utils/axios";

export const LoginContext = createContext();

const Index = (props) => {
  const [isLogin, setIsLogin] = useState(false);

  return (
    <LoginContext.Provider value={{ isLogin, setIsLogin }}>
      {props.children}
    </LoginContext.Provider>
  );
};
export default Index;
