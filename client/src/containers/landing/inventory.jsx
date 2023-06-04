import React, { useEffect, useState } from "react";
import { Route } from "react-router-dom";

import {
  HomeOutlined,
  DatabaseOutlined,
  WalletOutlined,
} from "@ant-design/icons";
import {
  StyledSubMenu,
  StyledMenuItem,
  StyledMenu,
} from "../landing/styles/main.styles";

import Home from "../inventoryModule/home";
import Seed from "../inventoryModule/seed";
import Onboard from "../inventoryModule/onboardedDevices";
import PNCodeStats from "../inventoryModule/pnCodeStats";

import Sites from "../inventoryModule/inventory/sites";
import Racks from "../inventoryModule/inventory/racks";
import Devices from "../inventoryModule/inventory/devices";
import Boards from "../inventoryModule/inventory/boards";
import SubBoards from "../inventoryModule/inventory/subBoards";
import SFPs from "../inventoryModule/inventory/sfps";
import Licenses from "../inventoryModule/inventory/licenses";
import SNTC from "../inventoryModule/inventory/sntc";
import REBD from "../inventoryModule/inventory/rebd";
import POS from "../inventoryModule/inventory/pos";
import Functions from "../inventoryModule/inventory/functions";
import Domains from "../inventoryModule/inventory/domains";
import CDN from "../inventoryModule/inventory/cdn";
import PowerFeeds from "../inventoryModule/inventory/powerFeeds";

import EDNNetDashboard from "../inventoryModule/dashboards/ednNet";
import IGWNETDashboard from "../inventoryModule/dashboards/igwNet";
import EDNSYSDashboard from "../inventoryModule/dashboards/ednSys";
import IGWSysDashboard from "../inventoryModule/dashboards/igwSys";
import SOCDashboard from "../inventoryModule/dashboards/soc";

// import EDNVulnerabilityDashboard from "../inventoryModule/vulnerability/edn/dashboard";
// import EDNVulnerabilityMaster from "../inventoryModule/vulnerability/edn/master";
// import EDNVulnerabilityArcher from "../inventoryModule/vulnerability/edn/archer";
// import EDNVulnerabilityNotFoundDevices from "../inventoryModule/vulnerability/edn/notFoundDevices";
// import EDNVulnerabilityNoPlanDevices from "../inventoryModule/vulnerability/edn/noPlanDevices";

// import IGWVulnerabilityDashboard from "../inventoryModule/vulnerability/igw/dashboard";
// import IGWVulnerabilityMaster from "../inventoryModule/vulnerability/igw/master";
// import IGWVulnerabilityArcher from "../inventoryModule/vulnerability/igw/archer";
// import IGWVulnerabilityNotFoundDevices from "../inventoryModule/vulnerability/igw/notFoundDevices";
// import IGWVulnerabilityNoPlanDevices from "../inventoryModule/vulnerability/igw/noPlanDevices";

import IOSTracker from "../inventoryModule/trackers/edn/iosTracker";
import EDNPowerOffTracker from "../inventoryModule/trackers/edn/powerOffTracker";
import EDNHandbackTracker from "../inventoryModule/trackers/edn/handbackTracker";
import EDNHandoverTracker from "../inventoryModule/trackers/edn/handoverTracker";
import PMRTracker from "../inventoryModule/trackers/edn/pmrTracker";
import Snags from "../inventoryModule/trackers/edn/snags";
import CMDBTracker from "../inventoryModule/trackers/cmdbTracker";
import Backups from "../inventoryModule/backups";

export const InventoryMenu = ({ user, roles, history, location }) => {
  return (
    <>
      <StyledMenu
        user={user?.user_role}
        defaultSelectedKeys={["/"]}
        selectedKeys={[`/${location.pathname.split("/")[1]}`]}
        mode="inline"
        inlineCollapsed={false}
      >
        <StyledMenuItem
          key="/"
          icon={<HomeOutlined />}
          onClick={() => history.push("/")}
        >
          Home
        </StyledMenuItem>
        {user?.user_role !== roles.executive ? (
          <>
            {user?.user_role !== roles.user ? (
              <>
                <StyledMenuItem
                  key="/seed"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/seed")}
                >
                  Seed Devices
                </StyledMenuItem>
                {/* <StyledMenuItem
                  key="/staticonboarding"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/staticonboarding")}
                >
                  Static Onboarding
                </StyledMenuItem> */}
              </>
            ) : null}

            <StyledSubMenu
              user={user?.user_role}
              style={{ color: "white" }}
              key="sub1"
              icon={<DatabaseOutlined />}
              title="Inventory"
            >
              <StyledMenuItem
                key="/powerfeeds"
                icon={<WalletOutlined />}
                onClick={() => history.push("/powerfeeds")}
              >
                Power Feeds
              </StyledMenuItem>
              <StyledMenuItem
                key="/sntc"
                icon={<WalletOutlined />}
                onClick={() => history.push("/sntc")}
              >
                SNTC
              </StyledMenuItem>
              {/* <StyledMenuItem
                key="/iptendpoints"
                icon={<WalletOutlined />}
                onClick={() => history.push("/iptendpoints")}
              >
                IPT Endpoints
              </StyledMenuItem> */}
              <StyledMenuItem
                key="/cdn"
                icon={<WalletOutlined />}
                onClick={() => history.push("/cdn")}
              >
                CDN
              </StyledMenuItem>
              <StyledMenuItem
                key="/sites"
                icon={<WalletOutlined />}
                onClick={() => history.push("/sites")}
              >
                Sites
              </StyledMenuItem>
              <StyledMenuItem
                key="/racks"
                icon={<WalletOutlined />}
                onClick={() => history.push("/racks")}
              >
                Racks
              </StyledMenuItem>
              <StyledMenuItem
                key="/devices"
                icon={<WalletOutlined />}
                onClick={() => history.push("/devices")}
              >
                Devices
              </StyledMenuItem>
              <StyledMenuItem
                key="/boards"
                icon={<WalletOutlined />}
                onClick={() => history.push("/boards")}
              >
                Boards
              </StyledMenuItem>
              <StyledMenuItem
                key="/subboards"
                icon={<WalletOutlined />}
                onClick={() => history.push("/subboards")}
              >
                SubBoards
              </StyledMenuItem>
              <StyledMenuItem
                key="/sfps"
                icon={<WalletOutlined />}
                onClick={() => history.push("/sfps")}
              >
                SFPs
              </StyledMenuItem>
              <StyledMenuItem
                key="/licenses"
                icon={<WalletOutlined />}
                onClick={() => history.push("/licenses")}
              >
                Licenses
              </StyledMenuItem>
              <StyledMenuItem
                key="/rebd"
                icon={<WalletOutlined />}
                onClick={() => history.push("/rebd")}
              >
                REBD
              </StyledMenuItem>
              <StyledMenuItem
                key="/pos"
                icon={<WalletOutlined />}
                onClick={() => history.push("/pos")}
              >
                POS
              </StyledMenuItem>
              {user?.user_role === roles.admin ? (
                <>
                  <StyledMenuItem
                    key="/functions"
                    icon={<WalletOutlined />}
                    onClick={() => history.push("/functions")}
                  >
                    Functions
                  </StyledMenuItem>
                  <StyledMenuItem
                    key="/domains"
                    icon={<WalletOutlined />}
                    onClick={() => history.push("/domains")}
                  >
                    Domains
                  </StyledMenuItem>
                </>
              ) : null}
            </StyledSubMenu>

            <StyledSubMenu
              user={user?.user_role}
              style={{ color: "white" }}
              key="sub3-2"
              icon={<DatabaseOutlined />}
              title="Trackers"
            >
              <StyledMenuItem
                key="/cmdbtracker"
                icon={<WalletOutlined />}
                onClick={() => history.push("/cmdbtracker")}
              >
                CMDB Tracker
              </StyledMenuItem>
              <StyledSubMenu
                style={{ color: "white" }}
                key="itservicemapping"
                icon={<DatabaseOutlined />}
                title="EDN"
              >
                <StyledMenuItem
                  key="/iostracker"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/iostracker")}
                >
                  IOS Tracker
                </StyledMenuItem>
                <StyledMenuItem
                  key="/ednpowerofftracker"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/ednpowerofftracker")}
                >
                  Power Off Tracker
                </StyledMenuItem>
                <StyledMenuItem
                  key="/ednhandbacktracker"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/ednhandbacktracker")}
                >
                  Handback Tracker
                </StyledMenuItem>
                <StyledMenuItem
                  key="/ednhandovertracker"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/ednhandovertracker")}
                >
                  Handover Tracker
                </StyledMenuItem>
                <StyledMenuItem
                  key="/pmrtracker"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/pmrtracker")}
                >
                  PMR Tracker
                </StyledMenuItem>
                <StyledMenuItem
                  key="/snags"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/snags")}
                >
                  Snags
                </StyledMenuItem>
              </StyledSubMenu>
            </StyledSubMenu>

            <StyledMenuItem
              key="/onboard"
              icon={<WalletOutlined />}
              onClick={() => history.push("/onboard")}
            >
              OnBoarded Devices
            </StyledMenuItem>
            <StyledMenuItem
              key="/pncodestats"
              icon={<WalletOutlined />}
              onClick={() => history.push("/pncodestats")}
            >
              PN Code Stats
            </StyledMenuItem>
          </>
        ) : null}

        <StyledSubMenu
          style={{ color: "white", paddingBottom: "380px" }}
          key="dashboards"
          icon={<DatabaseOutlined />}
          title="Dashboards"
        >
          <StyledMenuItem
            key="/ednnetdashboard"
            icon={<WalletOutlined />}
            onClick={() => history.push("/ednnetdashboard")}
          >
            EDN Net
          </StyledMenuItem>
          <StyledMenuItem
            key="/igwnetdashboard"
            icon={<WalletOutlined />}
            onClick={() => history.push("/igwnetdashboard")}
          >
            IGW Net
          </StyledMenuItem>
          <StyledMenuItem
            key="/ednsysdashboard"
            icon={<WalletOutlined />}
            onClick={() => history.push("/ednsysdashboard")}
          >
            EDN Sys
          </StyledMenuItem>
          <StyledMenuItem
            key="/igwsysdashboard"
            icon={<WalletOutlined />}
            onClick={() => history.push("/igwsysdashboard")}
          >
            IGW Sys
          </StyledMenuItem>
          <StyledMenuItem
            key="/socdashboard"
            icon={<WalletOutlined />}
            onClick={() => history.push("/socdashboard")}
          >
            SOC
          </StyledMenuItem>
        </StyledSubMenu>
        {/* <StyledMenuItem
          key="/backups"
          icon={<WalletOutlined />}
          onClick={() => history.push("/backups")}
        >
          Backup
        </StyledMenuItem> */}
        {/* <StyledSubMenu
          style={{ color: "white" }}
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
              onClick={() => history.push("/ednvulnerabilitynotfounddevices")}
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
          </StyledSubMenu>
          <StyledSubMenu
            style={{ color: "white", paddingBottom: "500px" }}
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
              onClick={() => history.push("/igwvulnerabilitynotfounddevices")}
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
        </StyledSubMenu> */}
      </StyledMenu>
    </>
  );
};

export const InventoryRoutes = ({ user, roles }) => {
  return (
    <>
      {user?.user_role !== roles.ednSM ? (
        <>
          <Route exact path="/" component={Home} />
          <Route exact path="/ednnetdashboard" component={EDNNetDashboard} />
          <Route exact path="/igwnetdashboard" component={IGWNETDashboard} />
          <Route exact path="/ednsysdashboard" component={EDNSYSDashboard} />
          <Route exact path="/igwsysdashboard" component={IGWSysDashboard} />
          <Route exact path="/socdashboard" component={SOCDashboard} />

          {user?.user_role !== roles.executive ? (
            <>
              <Route exact path="/onboard" component={Onboard} />
              <Route exact path="/sites" component={Sites} />
              <Route exact path="/sntc" component={SNTC} />
              <Route exact path="/racks" component={Racks} />
              <Route exact path="/rebd" component={REBD} />
              <Route exact path="/pos" component={POS} />
              <Route exact path="/devices" component={Devices} />
              <Route exact path="/boards" component={Boards} />
              <Route exact path="/subboards" component={SubBoards} />
              <Route exact path="/sfps" component={SFPs} />
              <Route exact path="/licenses" component={Licenses} />
              <Route exact path="/pncodestats" component={PNCodeStats} />
              <Route exact path="/cdn" component={CDN} />
              <Route exact path="/powerfeeds" component={PowerFeeds} />
              <Route exact path="/iostracker" component={IOSTracker} />
              <Route
                exact
                path="/ednpowerofftracker"
                component={EDNPowerOffTracker}
              />
              <Route
                exact
                path="/ednhandbacktracker"
                component={EDNHandbackTracker}
              />
              <Route
                exact
                path="/ednhandovertracker"
                component={EDNHandoverTracker}
              />
              <Route exact path="/pmrtracker" component={PMRTracker} />
              <Route exact path="/snags" component={Snags} />
              <Route exact path="/backups" component={Backups} />
              <Route exact path="/cmdbtracker" component={CMDBTracker} />

              {user?.user_role !== roles.user ? (
                <>
                  <Route exact path="/seed" component={Seed} />
                  {/* <Route
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
                  /> */}
                </>
              ) : null}
            </>
          ) : null}
        </>
      ) : null}
      {user?.user_role === roles.admin ? (
        <>
          <Route exact path="/functions" component={Functions} />
          <Route exact path="/domains" component={Domains} />
        </>
      ) : null}
    </>
  );
};
