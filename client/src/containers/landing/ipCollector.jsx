import React, { useEffect, useState } from "react";
import { Route } from "react-router-dom";
import { WalletOutlined } from "@ant-design/icons";
import EDNIPAM from "../ipCollectorModule/EDNIPAM";
import EDNIPAMDashboard from "../ipCollectorModule/EDNDashboard";
import IGWIPAMDashboard from "../ipCollectorModule/IGWDashboard";
import IGWIPAM from "../ipCollectorModule/IGWIPAM";
import SOCIpCollector from "../ipCollectorModule/SOC";
import { StyledMenuItem, StyledMenu } from "../landing/styles/main.styles";

export const IPCollectorMenu = ({ user, roles, history, location }) => {
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
                key="/ednipamdashboard"
                icon={<WalletOutlined />}
                onClick={() => history.push("/ednipamdashboard")}
              >
                EDN Dashboard
              </StyledMenuItem>
              <StyledMenuItem
                key="/igwipamdashboard"
                icon={<WalletOutlined />}
                onClick={() => history.push("/igwipamdashboard")}
              >
                IGW Dashboard
              </StyledMenuItem>
              <StyledMenuItem
                key="/ednipam"
                icon={<WalletOutlined />}
                onClick={() => history.push("/ednipam")}
              >
                EDN
              </StyledMenuItem>
              <StyledMenuItem
                key="/igwipam"
                icon={<WalletOutlined />}
                onClick={() => history.push("/igwipam")}
              >
                IGW
              </StyledMenuItem>
              <StyledMenuItem
                key="/socipcollector"
                icon={<WalletOutlined />}
                onClick={() => history.push("/socipcollector")}
              >
                SOC
              </StyledMenuItem>
            </>
          ) : null}
        </>
      </StyledMenu>
    </>
  );
};

export const IPCollectorRoutes = ({ user, roles }) => {
  return (
    <>
      {user?.user_role !== roles.ednSM ? (
        <>
          {user?.user_role !== roles.executive ? (
            <>
              <Route exact path="/ednipam" component={EDNIPAM} />
              <Route
                exact
                path="/ednipamdashboard"
                component={EDNIPAMDashboard}
              />
              <Route exact path="/igwipam" component={IGWIPAM} />
              <Route
                exact
                path="/igwipamdashboard"
                component={IGWIPAMDashboard}
              />
              <Route exact path="/socipcollector" component={SOCIpCollector} />
            </>
          ) : null}
        </>
      ) : null}
    </>
  );
};
