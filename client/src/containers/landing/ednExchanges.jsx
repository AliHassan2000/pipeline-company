import React, { useEffect, useState } from "react";
import { Route } from "react-router-dom";
import { WalletOutlined } from "@ant-design/icons";
import { StyledMenuItem, StyledMenu } from "../landing/styles/main.styles";
import EDNExchangeDashboard from "../ednExchangeModule/dashboard";
import EDNExchange from "../ednExchangeModule/exchange";
import EDNCoreRouting from "../ednExchangeModule/coreRouting";
import VRFOwners from "../ednExchangeModule/vrfOwners";
import ExternalVRFAnalysis from "../ednExchangeModule/externalVRFAnalysis";
import IntranetVRFAnalysis from "../ednExchangeModule/intranetVRFAnalysis";
import ReceivedRoutes from "../ednExchangeModule/receivedRoutes";

export const EDNExchangesMenu = ({ user, roles, history, location }) => {
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
                key="/ednexchangedashboard"
                icon={<WalletOutlined />}
                onClick={() => history.push("/ednexchangedashboard")}
              >
                EDN Exchange Dashboard
              </StyledMenuItem>
              <StyledMenuItem
                key="/ednexchange"
                icon={<WalletOutlined />}
                onClick={() => history.push("/ednexchange")}
              >
                EDN Exchange
              </StyledMenuItem>
              <StyledMenuItem
                key="/edncorerouting"
                icon={<WalletOutlined />}
                onClick={() => history.push("/edncorerouting")}
              >
                EDN Core Routing
              </StyledMenuItem>
              <StyledMenuItem
                key="/vrfowners"
                icon={<WalletOutlined />}
                onClick={() => history.push("/vrfowners")}
              >
                VRF Owners
              </StyledMenuItem>
              <StyledMenuItem
                key="/externalvrfanalysis"
                icon={<WalletOutlined />}
                onClick={() => history.push("/externalvrfanalysis")}
              >
                Extranet VRF Analysis
              </StyledMenuItem>
              <StyledMenuItem
                key="/intranetvrfanalysis"
                icon={<WalletOutlined />}
                onClick={() => history.push("/intranetvrfanalysis")}
              >
                Intranet VRF Analysis
              </StyledMenuItem>
              <StyledMenuItem
                key="/received-routes"
                icon={<WalletOutlined />}
                onClick={() => history.push("/received-routes")}
              >
                Received Routes
              </StyledMenuItem>
            </>
          ) : null}
        </>
      </StyledMenu>
    </>
  );
};

export const EDNExchangesRoutes = ({ user, roles }) => {
  return (
    <>
      {user?.user_role !== roles.ednSM ? (
        <>
          <Route exact path="/ednexchange" component={EDNExchange} />
          <Route exact path="/edncorerouting" component={EDNCoreRouting} />
          <Route exact path="/vrfowners" component={VRFOwners} />
          <Route
            exact
            path="/externalvrfanalysis"
            component={ExternalVRFAnalysis}
          />
          <Route
            exact
            path="/intranetvrfanalysis"
            component={IntranetVRFAnalysis}
          />
          <Route exact path="/received-routes" component={ReceivedRoutes} />
          <Route
            exact
            path="/ednexchangedashboard"
            component={EDNExchangeDashboard}
          />
        </>
      ) : null}
    </>
  );
};
