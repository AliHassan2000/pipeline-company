import React, { useState, useEffect } from "react";
import { Menu, Dropdown, Button } from "antd";
import "antd/dist/antd.css";
import DetailsTable from "./detailsTable";
import { DownOutlined } from "@ant-design/icons";
import styled from "styled-components";

function DeviceInfo(props) {
  const { data } = props;

  let dataCenterData = data !== null && data.datacenter;
  const [modalData, setModalData] = useState(dataCenterData);

  useEffect(() => {
    setModalData(dataCenterData);
  }, [dataCenterData]);

  let deviceData = data !== null && data.device;
  let rackData = data !== null && data.rack;
  let licenseData = data !== null && data.license;
  let boardDetail = data !== null && data.board;
  let sfp = data !== null && data.sfp;
  let subboard = data !== null && data.subboard;
  console.log("data===>", data);

  const createMenu = (dataArray) => {
    if (Array.isArray(dataArray)) {
      let subMenu = [];
      dataArray.forEach((element) => {
        subMenu.push(
          <Menu.Item key="0" style={{ background: "white" }}>
            <div
              style={{
                color: "white",
                borderRadius: "3px",
                fontSize: "10px",
                background: "#009bdb",
                padding: "1px 0 1px 0",
              }}
              onClick={() => setModalData(element)}
            >
              {element.board_name}
            </div>
          </Menu.Item>
        );
      });

      const menu = <Menu>{subMenu}</Menu>;
      return menu;
    } else return null;
  };

  const createMenuLicense = (dataArray) => {
    if (Array.isArray(dataArray)) {
      let subMenu = [];
      dataArray.forEach((element) => {
        subMenu.push(
          <Menu.Item key="0" style={{ background: "white" }}>
            <div
              style={{
                color: "white",
                borderRadius: "3px",
                fontSize: "10px",
                background: "#009bdb",
                padding: "1px 0 1px 0",
              }}
              onClick={() => setModalData(element)}
            >
              {element.license_name}
            </div>
          </Menu.Item>
        );
      });

      const menu = <Menu>{subMenu}</Menu>;
      return menu;
    } else return null;
  };

  const createMenuSfp = (dataArray) => {
    if (Array.isArray(dataArray)) {
      let subMenu = [];
      dataArray.forEach((element) => {
        subMenu.push(
          <Menu.Item key="0" style={{ background: "white" }}>
            <div
              style={{
                color: "white",
                borderRadius: "3px",
                fontSize: "10px",
                background: "#009bdb",
                padding: "1px 0 1px 0",
              }}
              onClick={() => setModalData(element)}
            >
              {element.port_name}
            </div>
          </Menu.Item>
        );
      });

      const menu = <Menu>{subMenu}</Menu>;
      return menu;
    } else return null;
  };

  const createMenuSubboard = (dataArray) => {
    if (Array.isArray(dataArray)) {
      let subMenu = [];
      dataArray.forEach((element) => {
        subMenu.push(
          <Menu.Item key="0" style={{ background: "white" }}>
            <div
              style={{
                color: "white",
                borderRadius: "3px",
                fontSize: "10px",
                background: "#009bdb",
                padding: "1px 0 1px 0",
              }}
              onClick={() => setModalData(element)}
            >
              {element.subboard_name}
            </div>
          </Menu.Item>
        );
      });

      const menu = <Menu>{subMenu}</Menu>;
      return menu;
    } else return null;
  };

  return (
    <div style={{ height: "50vh", display: "flex" }}>
      <div style={{ width: "20%", display: "block" }}>
        <StyledButton onClick={() => setModalData(dataCenterData)}>
          Physical Site Details
        </StyledButton>
        <br />
        <StyledButton onClick={() => setModalData(deviceData)}>
          Device Details
        </StyledButton>
        <br />
        <StyledButton onClick={() => setModalData(rackData)}>
          Rack Details
        </StyledButton>
        <br />

        <StyledDropDown
          overlay={createMenuLicense(licenseData)}
          trigger={["click"]}
        >
          <div
            className="ant-dropdown-link"
            onClick={(e) => e.preventDefault()}
          >
            Licenses <DownOutlined />
          </div>
        </StyledDropDown>

        <StyledDropDown overlay={createMenu(boardDetail)} trigger={["click"]}>
          <div
            className="ant-dropdown-link"
            onClick={(e) => e.preventDefault()}
          >
            Board Details <DownOutlined />
          </div>
        </StyledDropDown>

        <StyledDropDown overlay={createMenuSfp(sfp)} trigger={["click"]}>
          <div
            className="ant-dropdown-link"
            onClick={(e) => e.preventDefault()}
          >
            SFP Details <DownOutlined />
          </div>
        </StyledDropDown>

        <StyledDropDown
          overlay={createMenuSubboard(subboard)}
          trigger={["click"]}
        >
          <div
            className="ant-dropdown-link"
            onClick={(e) => e.preventDefault()}
          >
            Sub Boards <DownOutlined />
          </div>
        </StyledDropDown>
      </div>
      <div
        style={{
          boxShadow: "rgba(99, 99, 99, 0.4) 0px 2px 8px 0px",

          // border: "2px solid #009bdb",
          width: "80%",
          overflowY: "scroll",
          padding: "12px 30px",
        }}
      >
        <DetailsTable detailsData={modalData} />
      </div>
    </div>
  );
}

const StyledDropDown = styled(Dropdown)`
  font-size: 11px;
  margin-bottom: 10px;
  width: 93%;
  font-family: Montserrat-Regular;
  font-weight: bold;
  background-color: #009bdb;
  color: white;
  padding: 6px 10px;
  border-radius: 5px;
  text-align: center;
  cursor: pointer;
`;
const StyledButton = styled(Button)`
  font-size: 11px;
  margin-bottom: 10px;
  width: 93%;
  font-family: Montserrat-Regular;
  font-weight: bold;
  background-color: #009bdb;
  color: white;
  padding: 6px 10px;
  border-radius: 5px;
`;

export default DeviceInfo;
