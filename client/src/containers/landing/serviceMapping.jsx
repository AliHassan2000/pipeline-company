import React, { useEffect, useState } from "react";
import { Route } from "react-router-dom";
import { DatabaseOutlined, WalletOutlined } from "@ant-design/icons";
import EdnNeList from "../serviceMappingModule/edn/nodeList/neList";
import EdnSecList from "../serviceMappingModule/edn/nodeList/secList";
// import EdnItList from "../serviceMappingModule/edn/nodeList/itList";
import EDNMACLegacy from "../serviceMappingModule/edn/mac";
import EDNMACLegacySearch from "../serviceMappingModule/edn/serviceMappingSearch";
import EDNARP from "../serviceMappingModule/edn/firewallARP";
import EDNServices from "../serviceMappingModule/edn/services";
import {
  StyledSubMenu,
  StyledMenuItem,
  StyledMenu,
} from "../landing/styles/main.styles";
import ServiceMappingDashboard from "../serviceMappingModule/edn/dashboards/serviceMapping";
import PhysicalServers from "../serviceMappingModule/edn/itServiceMapping/physicalServers";
import App from "../serviceMappingModule/edn/itServiceMapping/app";
import Os from "../serviceMappingModule/edn/itServiceMapping/os";
import Mac from "../serviceMappingModule/edn/itServiceMapping/mac";
import Ip from "../serviceMappingModule/edn/itServiceMapping/ip";
import Owner from "../serviceMappingModule/edn/itServiceMapping/owner";

export const ServiceMappingMenu = ({ user, roles, history, location }) => {
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
          {user?.user_role !== roles.executive &&
          user?.user_role !== roles.user &&
          user?.user_role !== roles.ednSM ? (
            <>
              <StyledSubMenu
                user={user?.user_role}
                style={{ color: "white" }}
                key="sub3-2"
                icon={<DatabaseOutlined />}
                title="EDN"
              >
                <StyledSubMenu
                  user={user?.user_role}
                  style={{ color: "white" }}
                  key="dashboards"
                  icon={<DatabaseOutlined />}
                  title="Dashboards"
                >
                  <StyledMenuItem
                    key="/servicemappingdashboard"
                    icon={<WalletOutlined />}
                    onClick={() => history.push("/servicemappingdashboard")}
                  >
                    Service Mapping
                  </StyledMenuItem>
                </StyledSubMenu>
                <StyledSubMenu
                  style={{ color: "white" }}
                  key="sub2"
                  icon={<DatabaseOutlined />}
                  title="EDN Node List"
                >
                  <StyledMenuItem
                    key="/nelist"
                    icon={<WalletOutlined />}
                    onClick={() => history.push("/nelist")}
                  >
                    EDN NE List
                  </StyledMenuItem>
                  <StyledMenuItem
                    key="/seclist"
                    icon={<WalletOutlined />}
                    onClick={() => history.push("/seclist")}
                  >
                    EDN SEC List
                  </StyledMenuItem>
                </StyledSubMenu>
                <StyledSubMenu
                  user={user?.user_role}
                  style={{ color: "white" }}
                  key="itservicemapping"
                  icon={<DatabaseOutlined />}
                  title="IT Service Mapping"
                >
                  <StyledMenuItem
                    key="/physicalservers"
                    icon={<WalletOutlined />}
                    onClick={() => history.push("/physicalservers")}
                  >
                    Physical Servers
                  </StyledMenuItem>
                  <StyledMenuItem
                    key="/app"
                    icon={<WalletOutlined />}
                    onClick={() => history.push("/app")}
                  >
                    App
                  </StyledMenuItem>
                  <StyledMenuItem
                    key="/os"
                    icon={<WalletOutlined />}
                    onClick={() => history.push("/os")}
                  >
                    Os
                  </StyledMenuItem>
                  <StyledMenuItem
                    key="/mac"
                    icon={<WalletOutlined />}
                    onClick={() => history.push("/mac")}
                  >
                    Mac
                  </StyledMenuItem>
                  <StyledMenuItem
                    key="/ip"
                    icon={<WalletOutlined />}
                    onClick={() => history.push("/ip")}
                  >
                    Ip
                  </StyledMenuItem>
                  <StyledMenuItem
                    key="/owner"
                    icon={<WalletOutlined />}
                    onClick={() => history.push("/owner")}
                  >
                    Owner
                  </StyledMenuItem>
                </StyledSubMenu>
                <StyledMenuItem
                  key="/ednmaclegacy"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/ednmaclegacy")}
                >
                  MAC
                </StyledMenuItem>
                <StyledMenuItem
                  key="/ednmaclegacysearch"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/ednmaclegacysearch")}
                >
                  Service Mapping Search
                </StyledMenuItem>
                <StyledMenuItem
                  key="/ednarp"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/ednarp")}
                >
                  Firewall ARP
                </StyledMenuItem>
                <StyledMenuItem
                  key="/ednservices"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/ednservices")}
                >
                  EDN Services
                </StyledMenuItem>
              </StyledSubMenu>
              <StyledSubMenu
                user={user?.user_role}
                style={{ color: "white", paddingBottom: "200px" }}
                key="igwsub"
                icon={<DatabaseOutlined />}
                title="IGW"
              ></StyledSubMenu>
            </>
          ) : null}

          {user?.user_role === roles.user ? (
            <>
              <StyledMenuItem
                key="/ednmaclegacy"
                icon={<WalletOutlined />}
                onClick={() => history.push("/ednmaclegacy")}
              >
                Edn Service Mapping
              </StyledMenuItem>
              <StyledMenuItem
                key="/ednmaclegacyseacrh"
                icon={<WalletOutlined />}
                onClick={() => history.push("/ednmaclegacysearch")}
              >
                Edn Service Mapping Search
              </StyledMenuItem>
              <StyledSubMenu
                user={user?.user_role}
                style={{ color: "white" }}
                key="itservicemapping"
                icon={<DatabaseOutlined />}
                title="IT Service Mapping"
              >
                <StyledMenuItem
                  key="/physicalservers"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/physicalservers")}
                >
                  Physical Servers
                </StyledMenuItem>
                <StyledMenuItem
                  key="/app"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/app")}
                >
                  App
                </StyledMenuItem>
                <StyledMenuItem
                  key="/os"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/os")}
                >
                  Os
                </StyledMenuItem>
                <StyledMenuItem
                  key="/mac"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/mac")}
                >
                  Mac
                </StyledMenuItem>
                <StyledMenuItem
                  key="/ip"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/ip")}
                >
                  Ip
                </StyledMenuItem>
                <StyledMenuItem
                  key="/owner"
                  icon={<WalletOutlined />}
                  onClick={() => history.push("/owner")}
                >
                  Owner
                </StyledMenuItem>
              </StyledSubMenu>
            </>
          ) : null}
        </>
      </StyledMenu>
    </>
  );
};

export const ServiceMappingRoutes = ({ user, roles }) => {
  return (
    <>
      {user?.user_role !== roles.ednSM &&
      user?.user_role !== roles.executive ? (
        <>
          <Route exact path="/physicalservers" component={PhysicalServers} />
          <Route exact path="/app" component={App} />
          <Route exact path="/os" component={Os} />
          <Route exact path="/mac" component={Mac} />
          <Route exact path="/ip" component={Ip} />
          <Route exact path="/owner" component={Owner} />

          <Route exact path="/ednmaclegacy" component={EDNMACLegacy} />
          <Route
            exact
            path="/ednmaclegacysearch"
            component={EDNMACLegacySearch}
          />

          {user?.user_role !== roles.user ? (
            <>
              <Route
                exact
                path="/servicemappingdashboard"
                component={ServiceMappingDashboard}
              />
              <Route exact path="/nelist" component={EdnNeList} />
              <Route exact path="/seclist" component={EdnSecList} />
              {/* <Route exact path="/itlist" component={EdnItList} /> */}
              <Route exact path="/ednservices" component={EDNServices} />
              <Route exact path="/ednarp" component={EDNARP} />
            </>
          ) : null}
        </>
      ) : null}
    </>
  );
};
