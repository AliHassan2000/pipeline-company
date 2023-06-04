import React, { useEffect, useState } from "react";
import { Route } from "react-router-dom";

import { DatabaseOutlined, WalletOutlined } from "@ant-design/icons";
import {
  StyledSubMenu,
  StyledMenuItem,
  StyledMenu,
} from "../landing/styles/main.styles";

// import SecurityOperationDashboard from "../cyberSecurityModule/dashboards/securityOperation";
import EDNDashboard from "../cyberSecurityModule/dashboards/edn";
import IGWDashboard from "../cyberSecurityModule/dashboards/igw";
import SOCDashboard from "../cyberSecurityModule/dashboards/soc";
import SYSDashboard from "../cyberSecurityModule/dashboards/sys";

import EDNVulnerabilityDashboard from "../cyberSecurityModule/vulnerability/edn/dashboard";
import EDNVulnerabilityMaster from "../cyberSecurityModule/vulnerability/edn/master";
import EDNVulnerabilityArcher from "../cyberSecurityModule/vulnerability/edn/archer";
import EDNVulnerabilityNotFoundDevices from "../cyberSecurityModule/vulnerability/edn/notFoundDevices";
import EDNVulnerabilityNoPlanDevices from "../cyberSecurityModule/vulnerability/edn/noPlanDevices";

import IGWVulnerabilityDashboard from "../cyberSecurityModule/vulnerability/igw/dashboard";
import IGWVulnerabilityMaster from "../cyberSecurityModule/vulnerability/igw/master";
import IGWVulnerabilityArcher from "../cyberSecurityModule/vulnerability/igw/archer";
import IGWVulnerabilityNotFoundDevices from "../cyberSecurityModule/vulnerability/igw/notFoundDevices";
import IGWVulnerabilityNoPlanDevices from "../cyberSecurityModule/vulnerability/igw/noPlanDevices";

import SOCVulnerabilityDashboard from "../cyberSecurityModule/vulnerability/soc/dashboard";
import SOCVulnerabilityMaster from "../cyberSecurityModule/vulnerability/soc/master";
import SOCVulnerabilityArcher from "../cyberSecurityModule/vulnerability/soc/archer";
import SOCVulnerabilityNotFoundDevices from "../cyberSecurityModule/vulnerability/soc/notFoundDevices";
import SOCVulnerabilityNoPlanDevices from "../cyberSecurityModule/vulnerability/soc/noPlanDevices";

import BulkUpdate from "../cyberSecurityModule/bulkUpdate";

export const CyberSecurityMenu = ({ user, roles, history, location }) => {
  return (
    <>
      <StyledMenu
        user={user?.user_role}
        defaultSelectedKeys={["/"]}
        selectedKeys={[`/${location.pathname.split("/")[1]}`]}
        mode="inline"
        inlineCollapsed={false}
      >
        {user?.user_role === roles.admin ||
        user?.user_role === roles.engineer ? (
          <>
            <StyledSubMenu
              style={{ color: "white" }}
              key="vulnerabilitydashboards"
              icon={<DatabaseOutlined />}
              title="Security Compliance"
            >
              <StyledMenuItem
                key="/securitycomplianceedndashboard"
                icon={<WalletOutlined />}
                onClick={() => history.push("/securitycomplianceedndashboard")}
              >
                EDN
              </StyledMenuItem>
              <StyledMenuItem
                key="/securitycomplianceigwdashboard"
                icon={<WalletOutlined />}
                onClick={() => history.push("/securitycomplianceigwdashboard")}
              >
                IGW
              </StyledMenuItem>
              <StyledMenuItem
                key="/securitycompliancesocdashboard"
                icon={<WalletOutlined />}
                onClick={() => history.push("/securitycompliancesocdashboard")}
              >
                SOC
              </StyledMenuItem>
              <StyledMenuItem
                key="/securitycompliancesystemdashboard"
                icon={<WalletOutlined />}
                onClick={() =>
                  history.push("/securitycompliancesystemdashboard")
                }
              >
                SYS
              </StyledMenuItem>
              <StyledMenuItem
                key="/bulkupdate"
                icon={<WalletOutlined />}
                onClick={() => history.push("/bulkupdate")}
              >
                Bulk Update
              </StyledMenuItem>
            </StyledSubMenu>
            <StyledSubMenu
              style={{ color: "white", paddingBottom: "200px" }}
              key="vulnerability"
              icon={<DatabaseOutlined />}
              title="Vulnerability"
            >
              <StyledSubMenu
                style={{ color: "white" }}
                key="ednvulnerability"
                icon={<DatabaseOutlined />}
                title="EDN"
              >
                <StyledMenuItem
                  key="/ednvulnerabilitydashboard"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/ednvulnerabilitydashboard")}
                >
                  Dashboard
                </StyledMenuItem>
                <StyledMenuItem
                  key="/ednvulnerabilitymaster"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/ednvulnerabilitymaster")}
                >
                  Master
                </StyledMenuItem>
                <StyledMenuItem
                  key="/ednvulnerabilityarcher"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/ednvulnerabilityarcher")}
                >
                  Archer
                </StyledMenuItem>
                <StyledMenuItem
                  key="/ednvulnerabilitynotfounddevices"
                  icon={<WalletOutlined />}
                  onClick={() =>
                    history.push("/ednvulnerabilitynotfounddevices")
                  }
                >
                  Not Found Devices
                </StyledMenuItem>
                <StyledMenuItem
                  key="/ednvulnerabilitynoplandevices"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/ednvulnerabilitynoplandevices")}
                >
                  No Plan Devices
                </StyledMenuItem>
                {/* <StyledMenuItem
              key="/ednvulnerabilityinprogress"
              icon={<WalletOutlined />}
              onClick={() => history.push("/ednvulnerabilityinprogress")}
            >
              Inprogress
            </StyledMenuItem>
            <StyledMenuItem
              key="/ednvulnerabilitymanagedby"
              icon={<WalletOutlined />}
              onClick={() => history.push("/ednvulnerabilitymanagedby")}
            >
              Managedby
            </StyledMenuItem>
            <StyledMenuItem
              key="/ednvulnerabilityopen"
              icon={<WalletOutlined />}
              onClick={() => history.push("/ednvulnerabilityopen")}
            >
              Open
            </StyledMenuItem>
            <StyledMenuItem
              key="/ednvulnerabilityoverdue"
              icon={<WalletOutlined />}
              onClick={() => history.push("/ednvulnerabilityoverdue")}
            >
              Overdue
            </StyledMenuItem> */}
              </StyledSubMenu>
              <StyledSubMenu
                style={{ color: "white" }}
                key="igwvulnerability"
                icon={<DatabaseOutlined />}
                title="IGW"
              >
                <StyledMenuItem
                  key="/igwvulnerabilitydashboard"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/igwvulnerabilitydashboard")}
                >
                  Dashboard
                </StyledMenuItem>
                <StyledMenuItem
                  key="/igwvulnerabilitymaster"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/igwvulnerabilitymaster")}
                >
                  Master
                </StyledMenuItem>
                <StyledMenuItem
                  key="/igwvulnerabilityarcher"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/igwvulnerabilityarcher")}
                >
                  Archer
                </StyledMenuItem>
                <StyledMenuItem
                  key="/igwvulnerabilitynotfounddevices"
                  icon={<WalletOutlined />}
                  onClick={() =>
                    history.push("/igwvulnerabilitynotfounddevices")
                  }
                >
                  Not Found Devices
                </StyledMenuItem>
                <StyledMenuItem
                  key="/igwvulnerabilitynoplandevices"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/igwvulnerabilitynoplandevices")}
                >
                  No Plan Devices
                </StyledMenuItem>
              </StyledSubMenu>

              <StyledSubMenu
                style={{ color: "white", paddingBottom: "500px" }}
                key="socvulnerability"
                icon={<DatabaseOutlined />}
                title="SOC"
              >
                <StyledMenuItem
                  key="/socvulnerabilitydashboard"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/socvulnerabilitydashboard")}
                >
                  Dashboard
                </StyledMenuItem>
                <StyledMenuItem
                  key="/socvulnerabilitymaster"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/socvulnerabilitymaster")}
                >
                  Master
                </StyledMenuItem>
                <StyledMenuItem
                  key="/socvulnerabilityarcher"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/socvulnerabilityarcher")}
                >
                  Archer
                </StyledMenuItem>
                <StyledMenuItem
                  key="/socvulnerabilitynotfounddevices"
                  icon={<WalletOutlined />}
                  onClick={() =>
                    history.push("/socvulnerabilitynotfounddevices")
                  }
                >
                  Not Found Devices
                </StyledMenuItem>
                <StyledMenuItem
                  key="/socvulnerabilitynoplandevices"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/socvulnerabilitynoplandevices")}
                >
                  No Plan Devices
                </StyledMenuItem>
              </StyledSubMenu>
            </StyledSubMenu>
          </>
        ) : null}
      </StyledMenu>
    </>
  );
};

export const CyberSecurityRoutes = ({ user, roles }) => {
  return (
    <>
      {user?.user_role === roles.admin || user?.user_role === roles.engineer ? (
        <>
          {/* <Route
            exact
            path="/securityoperationdashboard"
            component={SecurityOperationDashboard}
          /> */}
          <Route
            exact
            path="/securitycomplianceedndashboard"
            component={EDNDashboard}
          />
          <Route
            exact
            path="/securitycomplianceigwdashboard"
            component={IGWDashboard}
          />
          <Route
            exact
            path="/securitycompliancesocdashboard"
            component={SOCDashboard}
          />
          <Route
            exact
            path="/securitycompliancesystemdashboard"
            component={SYSDashboard}
          />
          <Route exact path="/bulkupdate" component={BulkUpdate} />
          <Route
            exact
            path="/ednvulnerabilitydashboard"
            component={EDNVulnerabilityDashboard}
          />
          <Route
            exact
            path="/ednvulnerabilitymaster"
            component={EDNVulnerabilityMaster}
          />
          <Route
            exact
            path="/ednvulnerabilityarcher"
            component={EDNVulnerabilityArcher}
          />
          <Route
            exact
            path="/ednvulnerabilitynotfounddevices"
            component={EDNVulnerabilityNotFoundDevices}
          />
          <Route
            exact
            path="/ednvulnerabilitynoplandevices"
            component={EDNVulnerabilityNoPlanDevices}
          />
          {/* <Route
                        exact
                        path="/ednvulnerabilityinprogress"
                        component={EDNVulnerabilityInProgress}
                      />
                      <Route
                        exact
                        path="/ednvulnerabilitymanagedby"
                        component={EDNVulnerabilityManagedBy}
                      />
                      <Route
                        exact
                        path="/ednvulnerabilityopen"
                        component={EDNVulnerabilityOpen}
                      />
                      <Route
                        exact
                        path="/ednvulnerabilityoverdue"
                        component={EDNVulnerabilityOverdue}
                      /> */}
          <Route
            exact
            path="/igwvulnerabilitydashboard"
            component={IGWVulnerabilityDashboard}
          />
          <Route
            exact
            path="/igwvulnerabilitymaster"
            component={IGWVulnerabilityMaster}
          />
          <Route
            exact
            path="/igwvulnerabilityarcher"
            component={IGWVulnerabilityArcher}
          />
          <Route
            exact
            path="/igwvulnerabilitynotfounddevices"
            component={IGWVulnerabilityNotFoundDevices}
          />
          <Route
            exact
            path="/igwvulnerabilitynoplandevices"
            component={IGWVulnerabilityNoPlanDevices}
          />

          <Route
            exact
            path="/socvulnerabilitydashboard"
            component={SOCVulnerabilityDashboard}
          />
          <Route
            exact
            path="/socvulnerabilitymaster"
            component={SOCVulnerabilityMaster}
          />
          <Route
            exact
            path="/socvulnerabilityarcher"
            component={SOCVulnerabilityArcher}
          />
          <Route
            exact
            path="/socvulnerabilitynotfounddevices"
            component={SOCVulnerabilityNotFoundDevices}
          />
          <Route
            exact
            path="/socvulnerabilitynoplandevices"
            component={SOCVulnerabilityNoPlanDevices}
          />
        </>
      ) : null}
    </>
  );
};
