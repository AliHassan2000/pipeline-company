import React, { useEffect, useState } from "react";
import { Route } from "react-router-dom";
import { DatabaseOutlined, WalletOutlined } from "@ant-design/icons";
import EDNToMPLS from "../physicalMappingModule/edn/EDNMPLS";
import EDNIPT from "../physicalMappingModule/edn/EDNIPT";
import EDNSystems from "../physicalMappingModule/edn/EDNSystems";
import IGWSystems from "../physicalMappingModule/igw/IGWSystems";
import Security from "../physicalMappingModule/edn/EDNSecurity";
import EDNCDPLegacy from "../physicalMappingModule/edn/cdpLegacy";
import EDNLLDPLegacy from "../physicalMappingModule/edn/lldp";
import EDNMACLegacy from "../serviceMappingModule/edn/mac";
import EDNMACLegacySearch from "../serviceMappingModule/edn/serviceMappingSearch";
import IGWServices from "../physicalMappingModule/igw/IGWServices";
import IGWLinks from "../physicalMappingModule/igw/IGWLinks";
import IGWCDPLegacy from "../physicalMappingModule/igw/cdpLegacy";
import IGWLLDPLegacy from "../physicalMappingModule/igw/lldp";
import IGWMACLegacy from "../physicalMappingModule/igw/mac";
import EDNMaster from "../physicalMappingModule/edn/master";
import IGWMaster from "../physicalMappingModule/igw/master";
import {
  StyledSubMenu,
  StyledMenuItem,
  StyledMenu,
} from "../landing/styles/main.styles";
import ServiceMappingDashboard from "../serviceMappingModule/edn/dashboards/serviceMapping";

export const PhysicalMappingMenu = ({ user, roles, history, location }) => {
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
              {user?.user_role !== roles.ednSM ? (
                <>
                  <StyledMenuItem
                    key="/ednmaster"
                    icon={<WalletOutlined />}
                    onClick={() => history.push("/ednmaster")}
                  >
                    EDN Mapping
                  </StyledMenuItem>
                  <StyledMenuItem
                    key="/igwmaster"
                    icon={<WalletOutlined />}
                    onClick={() => history.push("/igwmaster")}
                  >
                    IGW Mapping
                  </StyledMenuItem>
                </>
              ) : null}

              {user?.user_role !== roles.user &&
              user?.user_role !== roles.ednSM ? (
                <>
                  <StyledSubMenu
                    user={user?.user_role}
                    style={{ color: "white" }}
                    key="sub3-2"
                    icon={<DatabaseOutlined />}
                    title="EDN"
                  >
                    <StyledMenuItem
                      key="/edncdplegacy"
                      icon={<WalletOutlined />}
                      onClick={() => history.push("/edncdplegacy")}
                    >
                      CDP Legacy
                    </StyledMenuItem>
                    <StyledMenuItem
                      key="/ednlldplegacy"
                      icon={<WalletOutlined />}
                      onClick={() => history.push("/ednlldplegacy")}
                    >
                      LLDP
                    </StyledMenuItem>
                    <StyledMenuItem
                      key="/edntompls"
                      icon={<WalletOutlined />}
                      onClick={() => history.push("/edntompls")}
                    >
                      EDN MPLS
                    </StyledMenuItem>
                    <StyledMenuItem
                      key="/ednipt"
                      icon={<WalletOutlined />}
                      onClick={() => history.push("/ednipt")}
                    >
                      EDN IPT
                    </StyledMenuItem>
                    <StyledMenuItem
                      key="/ednsystems"
                      icon={<WalletOutlined />}
                      onClick={() => history.push("/ednsystems")}
                    >
                      EDN Systems
                    </StyledMenuItem>
                    <StyledMenuItem
                      key="/security"
                      icon={<WalletOutlined />}
                      onClick={() => history.push("/security")}
                    >
                      EDN Security
                    </StyledMenuItem>
                  </StyledSubMenu>
                </>
              ) : (
                <>
                  {user?.user_role === roles.user ? (
                    <>
                      <StyledMenuItem
                        key="/edndashboard"
                        icon={<WalletOutlined />}
                        onClick={() => history.push("/edndashboard")}
                      >
                        EDN Dashboard
                      </StyledMenuItem>
                    </>
                  ) : (
                    <>
                      <StyledMenuItem
                        key="/"
                        icon={<WalletOutlined />}
                        onClick={() => history.push("/")}
                      >
                        EDN Dashboard
                      </StyledMenuItem>
                      <StyledMenuItem
                        key="/ednmaclegacy"
                        icon={<WalletOutlined />}
                        onClick={() => history.push("/ednmaclegacy")}
                      >
                        Edn Service Mapping
                      </StyledMenuItem>
                      <StyledMenuItem
                        key="/ednmaclegacysearch"
                        icon={<WalletOutlined />}
                        onClick={() => history.push("/ednmaclegacysearch")}
                      >
                        Edn Service Mapping Search
                      </StyledMenuItem>
                    </>
                  )}
                </>
              )}
            </>
          ) : null}

          {user?.user_role !== roles.user && user?.user_role !== roles.ednSM ? (
            <>
              <StyledSubMenu
                style={{ color: "white", paddingBottom: "200px" }}
                key="sub3-1"
                icon={<DatabaseOutlined />}
                title="IGW"
              >
                <StyledMenuItem
                  key="/igwsystems"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/igwsystems")}
                >
                  IGW Systems
                </StyledMenuItem>
                <StyledMenuItem
                  key="/igwservices"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/igwservices")}
                >
                  IGW Services
                </StyledMenuItem>
                <StyledMenuItem
                  key="/igwlinks"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/igwlinks")}
                >
                  IGW Services DB
                </StyledMenuItem>
                <StyledMenuItem
                  key="/igwcdplegacy"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/igwcdplegacy")}
                >
                  CDP Legacy
                </StyledMenuItem>
                <StyledMenuItem
                  key="/igwlldplegacy"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/igwlldplegacy")}
                >
                  LLDP
                </StyledMenuItem>
                <StyledMenuItem
                  key="/igwmaclegacy"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/igwmaclegacy")}
                >
                  MAC
                </StyledMenuItem>
              </StyledSubMenu>
            </>
          ) : null}
        </>
      </StyledMenu>
    </>
  );
};

export const PhysicalMappingRoutes = ({ user, roles }) => {
  return (
    <>
      {user?.user_role === roles.ednSM ? (
        <>
          <Route exact path="/" component={ServiceMappingDashboard} />
          <Route exact path="/ednmaclegacy" component={EDNMACLegacy} />
          <Route
            exact
            path="/ednmaclegacysearch"
            component={EDNMACLegacySearch}
          />
        </>
      ) : (
        <Route exact path="/edndashboard" component={ServiceMappingDashboard} />
      )}

      {user?.user_role !== roles.ednSM &&
      user?.user_role !== roles.executive ? (
        <>
          <Route exact path="/ednmaster" component={EDNMaster} />
          <Route exact path="/igwmaster" component={IGWMaster} />

          {user?.user_role !== roles.user ? (
            <>
              {/* <Route exact path="/itlist" component={EdnItList} /> */}
              <Route exact path="/security" component={Security} />
              <Route exact path="/edntompls" component={EDNToMPLS} />
              <Route exact path="/ednipt" component={EDNIPT} />
              <Route exact path="/igwsystems" component={IGWSystems} />
              <Route exact path="/ednsystems" component={EDNSystems} />
              <Route exact path="/edncdplegacy" component={EDNCDPLegacy} />
              <Route exact path="/ednlldplegacy" component={EDNLLDPLegacy} />
              <Route exact path="/igwlldplegacy" component={IGWLLDPLegacy} />
              <Route exact path="/igwcdplegacy" component={IGWCDPLegacy} />
              <Route exact path="/igwmaclegacy" component={IGWMACLegacy} />
              <Route exact path="/igwservices" component={IGWServices} />
              <Route exact path="/igwlinks" component={IGWLinks} />
            </>
          ) : null}
        </>
      ) : null}
    </>
  );
};
