import React, { useEffect, useState } from "react";
import { Route } from "react-router-dom";
import { WalletOutlined } from "@ant-design/icons";
import DCEDN from "../dcCapacityModule/EDN";
import DCIGW from "../dcCapacityModule/IGW";
import DCEDNDashboard from "../dcCapacityModule/EDNDashboard";
import DCIGWDashboard from "../dcCapacityModule/IGWDashboard";
import { StyledMenuItem, StyledMenu } from "../landing/styles/main.styles";

export const DCCapacityMenu = ({ user, roles, history, location }) => {
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
          {!(user?.user_role === roles.executive) ? (
            <>
              <StyledMenuItem
                key="/dccapacityedndashboard"
                icon={<WalletOutlined />}
                onClick={() => history.push("/dccapacityedndashboard")}
              >
                EDN Dashboard
              </StyledMenuItem>
              <StyledMenuItem
                key="/dccapacityigwdashboard"
                icon={<WalletOutlined />}
                onClick={() => history.push("/dccapacityigwdashboard")}
              >
                IGW Dashboard
              </StyledMenuItem>
              <StyledMenuItem
                key="/dccapacityedn"
                icon={<WalletOutlined />}
                onClick={() => history.push("/dccapacityedn")}
              >
                EDN
              </StyledMenuItem>
              <StyledMenuItem
                key="/dccapacityigw"
                icon={<WalletOutlined />}
                onClick={() => history.push("/dccapacityigw")}
              >
                IGW
              </StyledMenuItem>
            </>
          ) : null}
        </>
      </StyledMenu>
    </>
  );
};

export const DCCapacityRoutes = ({ user, roles }) => {
  return (
    <>
      {user?.user_role !== roles.ednSM ? (
        <>
          {user?.user_role !== roles.executive ? (
            <>
              <Route exact path="/dccapacityigw" component={DCIGW} />
              <Route exact path="/dccapacityedn" component={DCEDN} />
              <Route
                exact
                path="/dccapacityedndashboard"
                component={DCEDNDashboard}
              />
              <Route
                exact
                path="/dccapacityigwdashboard"
                component={DCIGWDashboard}
              />
            </>
          ) : null}
        </>
      ) : null}
    </>
  );
};
