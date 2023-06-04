import React, { useEffect, useState } from "react";
import { Route } from "react-router-dom";
import { DatabaseOutlined, WalletOutlined } from "@ant-design/icons";
import IPTDashboard from "../iptModule/IPTDashboard";
import IPTEndpoints from "../iptModule/IPTEndpoints";
import {
  StyledSubMenu,
  StyledMenuItem,
  StyledMenu,
} from "../landing/styles/main.styles";
import IPTAssignmentTracker from "../iptModule/trackers/iptAssignmentTracker";
import IPTClearanceTracker from "../iptModule/trackers/iptClearanceTracker";
import IPTRMATracker from "../iptModule/trackers/RMATracker";

export const IPTMenu = ({ user, roles, history, location }) => {
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
          {user?.user_role !== roles.executive ? (
            <>
              <StyledMenuItem
                key="/iptdashboard"
                icon={<WalletOutlined />}
                onClick={() => history.push("/iptdashboard")}
              >
                IPT Dashboard
              </StyledMenuItem>
              <StyledMenuItem
                key="/iptendpoints"
                icon={<WalletOutlined />}
                onClick={() => history.push("/iptendpoints")}
              >
                IPT Endpoints
              </StyledMenuItem>
              <StyledSubMenu
                style={{ color: "white" }}
                key="trackers"
                icon={<DatabaseOutlined />}
                title="Trackers"
              >
                <StyledMenuItem
                  key="/iptassignmenttracker"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/iptassignmenttracker")}
                >
                  IPT Assignment Tracker
                </StyledMenuItem>
                <StyledMenuItem
                  key="/iptclearancetracker"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/iptclearancetracker")}
                >
                  IPT Clearance Tracker
                </StyledMenuItem>
                <StyledMenuItem
                  key="/iptrmatracker"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/iptrmatracker")}
                >
                  IPT RMA Tracker
                </StyledMenuItem>
              </StyledSubMenu>
            </>
          ) : null}
        </>
      </StyledMenu>
    </>
  );
};

export const IPTRoutes = ({ user, roles }) => {
  return (
    <>
      {user?.user_role !== roles.ednSM ? (
        <>
          {user?.user_role !== roles.executive ? (
            <>
              <Route exact path="/iptdashboard" component={IPTDashboard} />
              <Route exact path="/iptendpoints" component={IPTEndpoints} />
              <Route
                exact
                path="/iptassignmenttracker"
                component={IPTAssignmentTracker}
              />
              <Route exact path="/iptrmatracker" component={IPTRMATracker} />
              <Route
                exact
                path="/iptclearancetracker"
                component={IPTClearanceTracker}
              />
            </>
          ) : null}
        </>
      ) : null}
    </>
  );
};
