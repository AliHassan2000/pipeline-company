import styled from "styled-components";
import { Menu, Row, Col, Dropdown } from "antd";
import { Link, Route } from "react-router-dom";
const { SubMenu } = Menu;

export const StyledLogoutMenuItem = styled(Menu.Item)`
  text-align: center;
  font-weight: bold;
  font-family: Montserrat-Regular;
`;

export const StyledBar = styled.div`
  width: 100%;
  height: 50px;
  /* min-height: 56px; */
  background-color: #009bdb;
  display: flex;
  justify-content: space-between;
`;

export const StyledLogoLink = styled(Link)`
  width: 13%;
  margin: 0 0 5px 2%;
  padding: 3px 5px 0 5px;
  /* background: white; */
  border-radius: 5px;
  /* border: 1px solid black; */
`;
export const StyledUserNameContainer = styled.div`
  color: white;
  font-size: 120%;
  padding: 1% 6% 0 0;
`;

export const StyledMenuColumn = styled(Col)`
  position: fixed;
  z-index: 9;
  height: 100%;
  overflow: auto;
  /* width: 230px; */
  /* max-width: 250px; */
  width: 100%;
  background-color: #009bdb;
`;

export const StyledMenu = styled(Menu)`
  height: 100%;
  width: 100%;
  /* background-color: transparent; */
  /* background-color: #009bdb; */
  background-color: ${(props) =>
    props.user === "EDN-SM" ? "#2d5918 !important" : "#009bdb !important"};
  color: white;
  /* border: 1px solid black; */
`;
export const StyledBodyCol = styled(Col)`
  overflow: auto;
  height: 100%;
  width: 100%;
  padding: 40px 60px 0 30px;
  /* border: 1px solid black; */
`;

export const StyledSubMenu = styled(SubMenu)`
  .ant-menu {
    /* background-color: #009bdb !important; */
    background-color: ${(props) =>
      props.user === "EDN-SM" ? "#2d5918 !important" : "#009bdb !important"};
  }
  .ant-menu-submenu-arrow::after {
    color: white !important;
  }
  .ant-menu-submenu-arrow::before {
    color: white !important;
  }
`;

export const StyledMenuItem = styled(Menu.Item)`
  font-size: 12px;
  color: white;
  margin-top: 0px !important;
  border: none;
  &:hover {
    color: #009bdb !important;
    background-color: #8cd3ff !important;
  }
`;

export const StyledLink = styled(Link)`
  &:hover {
    color: #009bdb !important;
  }
`;
