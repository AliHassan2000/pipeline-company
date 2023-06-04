import React, { useState, useEffect } from "react";
import { UserOutlined, DownloadOutlined } from "@ant-design/icons";
import { Avatar, Menu, Dropdown } from "antd";
import { useHistory } from "react-router-dom";

export const NavIcons = (props) => {
  const history = useHistory();
  const [user, setUser] = useState();

  useEffect(() => {
    setUser(JSON.parse(localStorage.getItem("user")));
  }, []);

  const menu = (
    <Menu
      style={{
        marginTop: "-220px",
        width: "200px",
        height: "105px",
      }}
    >
      <Menu.Item
        key="0"
        style={{
          backgroundColor: "#009bdb",
          color: "white",
          fontSize: "13px",
          fontWeight: "bolder",
          padding: "5px 0 8px 0",
        }}
      >
        <a
          onClick={() => {
            // localStorage.removeItem("cisco_mobily_token");
            localStorage.removeItem("cisco_mobily_token_encrypted");
            localStorage.removeItem("module");
            localStorage.removeItem("user");
            setTimeout(() => {
              history.push("/");
              window.location.reload();
            }, 0);
          }}
        >
          Log Out
        </a>
      </Menu.Item>
      <Menu.Item
        key="0"
        style={{
          backgroundColor: "#009bdb",
          color: "white",
          fontSize: "13px",
          fontWeight: "bolder",
          padding: "5px 0 8px 0",
        }}
      >
        <a
          onClick={() => {
            props.setShowCPModal(true);
          }}
        >
          Change Password
        </a>
      </Menu.Item>
    </Menu>
  );

  return (
    <div
      style={{
        color: "white",
        fontSize: " 100%",
        padding: "12px 3% 0 0",
        // border: "1px solid black",
      }}
    >
      {user?.user_name} &nbsp;
      <Dropdown overlay={menu} trigger={["click"]}>
        <a className="ant-dropdown-link" onClick={(e) => e.preventDefault()}>
          <Avatar
            style={{
              backgroundColor: "white",
              color: "black",
            }}
            size={22}
            icon={<UserOutlined />}
          />
        </a>
      </Dropdown>
    </div>
  );
};
