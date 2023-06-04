import React, { useEffect, useState } from "react";
import { Route } from "react-router-dom";
import { WalletOutlined } from "@ant-design/icons";
import { StyledMenuItem, StyledMenu } from "../landing/styles/main.styles";
import F5 from "../f5Module/f5";
import F5Dashboard from "../f5Module/dashboard";

export const F5Menu = ({ user, roles, history, location }) => {
  return (
    <>
      <StyledMenu
        user={user?.user_role}
        defaultSelectedKeys={["/"]}
        selectedKeys={[`/${location.pathname.split("/")[1]}`]}
        mode="inline"
        inlineCollapsed={false}
      >
        <>
          <StyledMenuItem
            key="/f5dashboard"
            icon={<WalletOutlined />}
            onClick={() => history.push("/f5dashboard")}
          >
            F5 Dashboard
          </StyledMenuItem>
          <StyledMenuItem
            key="/f5"
            icon={<WalletOutlined />}
            onClick={() => history.push("/f5")}
          >
            F5
          </StyledMenuItem>
        </>
      </StyledMenu>
    </>
  );
};

export const F5Routes = ({ user, roles }) => {
  return (
    <>
      {user?.user_role !== roles.ednSM ? (
        <>
          {user?.user_role !== roles.executive ? (
            <>
              <Route exact path="/f5" component={F5} />
              <Route exact path="/f5dashboard" component={F5Dashboard} />
            </>
          ) : null}
        </>
      ) : null}
    </>
  );
};
