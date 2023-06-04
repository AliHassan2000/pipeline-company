import React, { useState, useRef, useEffect } from "react";
import {
  StyledPassword,
  StyledInput,
  StyledButton,
  StyledParagraph,
  StyledFormHeading,
  StyledLink,
  StyledSpan,
  StyledFormButtonWrapper,
  StyledForm,
  StyledFormItem,
  StyledFormCard,
  StyledImage,
  StyledContainer,
} from "./main.styles";
import { CloseOutlined } from "@ant-design/icons";
import { Link } from "react-router-dom";
import Logo from "../../resources/img2.png";

import { Divider, Row, Col, Spin, Button } from "antd";
import Checkbox from "antd/lib/checkbox/Checkbox";
import axios, { baseUrl } from "../../utils/axios";
import { useHistory, useLocation } from "react-router-dom";
import { roles } from "../../utils/constants.js";
import {
  storeEncryptedDataInLocalStorage,
  getDataFromLocalStorage,
} from "../../utils/encrypt";

const Index = (props) => {
  let history = useHistory();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState(null);
  const [password, setPassword] = useState(null);
  const [errors, setErrors] = useState([]);

  const getError = (error) => {
    return (
      <div
        style={{
          backgroundColor: "red",
          color: "white",
          padding: "3px 10px 3px 10px",
          borderRadius: "7px",
          marginBottom: "10px",
        }}
      >
        {error}{" "}
        <a
          style={{ color: "white", float: "right" }}
          onClick={() => setErrors([])}
        >
          <CloseOutlined style={{ color: "white" }} />
        </a>
      </div>
    );
  };

  const handleSubmit = async () => {
    console.log("in handleSubmit");

    let user = {
      user: email,
      pass: password,
    };

    await axios
      .post(`${baseUrl}/login`, user)
      .then((res) => {
        const promises = [];
        console.log(res);
        if (res.data.response === "Login Successful") {
          // localStorage.setItem("cisco_mobily_token", res.data["auth-key"]);
          storeEncryptedDataInLocalStorage(
            res.data["auth-key"],
            "cisco_mobily_token_encrypted"
          );

          promises.push(
            axios
              .get(baseUrl + "/getUserByToken")
              .then((response) => {
                localStorage.setItem("user", JSON.stringify(response.data));
                storeEncryptedDataInLocalStorage(
                  response.data,
                  "user_encrypted"
                );
                setTimeout(() => {
                  if (response.data?.user_role === roles?.ednSM) {
                    history.replace("/");
                  } else {
                    history.replace("/");
                  }
                  window.location.reload();
                }, 0);
                setLoading(false);
              })
              .catch((error) => {
                console.log(error);
                setLoading(false);
              })
          );
          setLoading(false);
          return Promise.all(promises);
        } else {
          setLoading(false);
          let e = getError("incorrect email or password");
          setErrors([e]);
        }
      })
      .catch((err) => {
        setLoading(false);
        let e = getError("incorrect email or password");
        setErrors([e]);
        console.log(err);
      });
  };

  return (
    <Spin tip="Loading..." spinning={loading}>
      <StyledContainer>
        <Row style={{ height: "100%" }}>
          <Col
            xs={{ span: 24 }}
            md={{ span: 24 }}
            lg={{ span: 16 }}
            xl={{ span: 10 }}
            style={{ margin: "auto" }}
          >
            <StyledFormCard>
              <Link to="/">
                <StyledImage src={Logo}></StyledImage>
              </Link>

              <StyledFormHeading
                style={{ textAlign: "center", fontWeight: "bolder" }}
              >
                Sign In Form
              </StyledFormHeading>

              <Divider style={{ backgroundColor: "white" }}></Divider>
              <StyledForm
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSubmit();
                }}
              >
                {errors.length > 0 ? errors : null}

                <StyledFormItem
                  wrapperCol={{ span: 24 }}
                  style={{ paddingTop: "0" }}
                  name="email"
                  required
                >
                  <StyledSpan style={{ color: "white" }}>
                    User Id<StyledSpan style={{ color: "red" }}> *</StyledSpan>
                  </StyledSpan>
                  <StyledInput
                    placeholder="email"
                    required
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                    }}
                  />
                </StyledFormItem>

                <StyledFormItem
                  wrapperCol={{ span: 24 }}
                  name="password"
                  required
                >
                  <StyledSpan style={{ color: "white" }}>
                    Password
                    <StyledSpan style={{ color: "red" }}> *</StyledSpan>
                  </StyledSpan>
                  <StyledPassword
                    placeholder="Password"
                    required={true}
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                    }}
                  />
                </StyledFormItem>
                <br />
                <StyledFormButtonWrapper>
                  <StyledButton
                    style={{ width: "100%", height: "2rem" }}
                    type="primary"
                    htmlType="submit"
                  >
                    Sign In
                  </StyledButton>
                </StyledFormButtonWrapper>
              </StyledForm>
            </StyledFormCard>
          </Col>
        </Row>
      </StyledContainer>
    </Spin>
  );
};

export default Index;
