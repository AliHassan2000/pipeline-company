import styled from "styled-components";
import { Form, Input, Button } from "antd";
import { Link } from "react-router-dom";

export const StyledPassword = styled(Input.Password)`
  font-family: Montserrat-Regular;
  height: 1.7rem;
  width: 100%;
  background-color: ${(props) => props.theme.colors.default};
  border-radius: 5px;
  box-shadow: 0 0 0 1.5px #ddd;
  margin-top: 5px;
  input {
    font-size: 11px;
    font-family: Montserrat-Regular !important;
    background-color: ${(props) => props.theme.colors.default} !important;
  }
`;

export const StyledInput = styled(Input)`
  font-size: 11px;
  font-family: ${(props) => props.theme.fontFamily.primary} !important;
  height: 1.7rem;
  width: 100%;
  background-color: ${(props) => props.theme.colors.default};
  border-radius: 5px;
  box-shadow: 0 0 0 1.5px #ddd;
  margin-top: 5px;
`;

export const StyledButton = styled(Button)`
  font-size: 12px;
  width: 100%;
  height: 2rem;
  font-family: Montserrat-Regular;
  font-weight: bolder;
  background-color: white;
  border-color: white;
  color: #009bdb;
  border-radius: 10px;
  padding: 0px 2rem 0 2rem;
  &:focus,
  &:hover {
    box-shadow: rgba(50, 50, 93, 0.25) 0px 13px 27px -5px,
      rgba(0, 0, 0, 0.3) 0px 8px 16px -8px;
    background-color: #009bdb;
    border-color: white;
    color: white;
  }
`;

export const StyledFormHeading = styled.h2`
  font-family: Montserrat-Regular;
  color: white;
`;

export const StyledParagraph = styled.p`
  font-size: 12px;
  font-family: Montserrat-Regular;
  color: white;
`;

export const StyledLink = styled(Link)`
  font-family: Montserrat-Regular;
  color: white;
  &:hover {
    color: #009bdb;
  }
`;

export const StyledSpan = styled.span`
  font-size: 12px;
  font-family: Montserrat-Regular;
`;

export const StyledFormButtonWrapper = styled(Form.Item)`
  padding: 0.5rem 0 0 0;
`;

export const StyledForm = styled.form`
  text-align: left;
`;

export const StyledFormItem = styled(Form.Item)`
  margin: auto;
  padding: 0.2rem 0 0.2rem 0;
  width: 100%;
  @media (max-width: 450px) {
    width: 100%;
  }
`;

export const StyledFormCard = styled.div`
  height: 70%;
  margin: auto;
  width: 70%;
  background-color: #009bdb;
  border-radius: 20px;
  padding: 20px;
  box-shadow: rgba(50, 50, 93, 0.25) 0px 50px 100px -20px,
    rgba(0, 0, 0, 0.3) 0px 30px 60px -30px,
    rgba(10, 37, 64, 0.35) 0px -2px 6px 0px inset;
  @media (max-width: 500px) {
    width: 85%;
  }
  @media (min-width: 700px) {
    width: 60%;
  }
`;

export const StyledImage = styled.img`
  border-radius: 10px;
  height: 100%;
  width: 100%;
  margin-bottom: 15px;
  background-color: #009bdb;
  padding: 8px 10% 8px 10%;
`;

export const StyledContainer = styled.div`
  background-color: white;
  height: 100vh;
`;
/* background-image: url(${Bg}); */
