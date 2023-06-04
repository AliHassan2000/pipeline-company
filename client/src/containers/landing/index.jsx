import React, { useEffect, useState, useRef } from "react";
import axios, { baseUrl } from "../../utils/axios";
import { Menu, Row, Col, Dropdown } from "antd";
import { useLocation, useHistory } from "react-router-dom";
import { NavIcons } from "../navIcons";
import { StyledImage } from "../../components/image/main.styles";
import Logo from "../../resources/img2.png";
import ServiceMappingLogo from "../../resources/serviceMappingLogo.png";
import {
  StyledBar,
  StyledLogoLink,
  StyledBodyCol,
  StyledLink,
  StyledMenuColumn,
  StyledSubMenu,
  StyledMenuItem,
  StyledUserNameContainer,
  StyledMenu,
  StyledLogoutMenuItem,
} from "../landing/styles/main.styles";
import { roles } from "../../utils/constants.js";
import CPModal from "./cPModal";
import { InventoryMenu, InventoryRoutes } from "./inventory";
import { CyberSecurityMenu, CyberSecurityRoutes } from "./cyberSecurity";
import { AccessPointsMenu, AccessPointsRoutes } from "./accessPoints";
import { F5Menu, F5Routes } from "./f5";
import { IPTMenu, IPTRoutes } from "./ipt";
import { DCCapacityMenu, DCCapacityRoutes } from "./dcCapacity";
import { IPCollectorMenu, IPCollectorRoutes } from "./ipCollector";
import { IPAMMenu, IPAMRoutes } from "./ipam";
import { EDNExchangesMenu, EDNExchangesRoutes } from "./ednExchanges";
import { ServiceMappingMenu, ServiceMappingRoutes } from "./serviceMapping";
import { PhysicalMappingMenu, PhysicalMappingRoutes } from "./physicalMapping";
import { AdminMenu, AdminRoutes } from "./admin";

let userInfo = JSON.parse(localStorage.getItem("user"));

const Index = (props) => {
  useEffect(() => {
    setUser(JSON.parse(localStorage.getItem("user")));
  }, []);

  const location = useLocation();
  const history = useHistory();
  const [user, setUser] = useState();
  const [showCPModal, setShowCPModal] = useState(false);
  const [module, setModule] = useState(
    localStorage.getItem("module")
      ? localStorage.getItem("module")
      : userInfo?.user_role === roles?.ednSM
      ? "physicalmapping"
      : "inventorymodule"
  );

  let barColor =
    baseUrl === "https://localhost:5000"
      ? "orange"
      : userInfo?.user_role === roles?.ednSM
      ? "#2d5918"
      : "#009bdb";

  return (
    <>
      <StyledBar
        style={{ position: "fixed", zIndex: "999", backgroundColor: barColor }}
      >
        <StyledLogoLink to="/">
          <StyledImage
            src={user?.user_role === roles.ednSM ? ServiceMappingLogo : Logo}
          ></StyledImage>
        </StyledLogoLink>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            width: "55%",
          }}
        >
          <StyledMenu
            user={user?.user_role}
            selectedKeys={[`${module}`]}
            mode="horizontal"
            inlineCollapsed={false}
            overflowedIndicator={<span>More...</span>}
          >
            {user?.user_role !== roles.ednSM ? (
              <>
                <StyledMenuItem
                  key="inventorymodule"
                  onClick={() => {
                    setModule("inventorymodule");
                    localStorage.setItem("module", "inventorymodule");
                    history.push("/");
                  }}
                >
                  Inventory
                </StyledMenuItem>
                <StyledMenuItem
                  key="physicalmapping"
                  onClick={() => {
                    setModule("physicalmapping");
                    localStorage.setItem("module", "physicalmapping");
                    console.log("edn sm tag ===>");
                    console.log(user, roles);
                    history.push("/ednmaster");
                  }}
                >
                  Physical Mapping
                </StyledMenuItem>
                <StyledMenuItem
                  key="servicemapping"
                  onClick={() => {
                    setModule("servicemapping");
                    localStorage.setItem("module", "servicemapping");
                    history.push("/servicemappingdashboard");
                  }}
                >
                  Service Mapping
                </StyledMenuItem>
                <StyledMenuItem
                  key="dccapacity"
                  onClick={() => {
                    setModule("dccapacity");
                    localStorage.setItem("module", "dccapacity");
                    history.push("/dccapacityedndashboard");
                  }}
                >
                  DC Capacity
                </StyledMenuItem>
                <StyledMenuItem
                  key="ipcollector"
                  onClick={() => {
                    setModule("ipcollector");
                    localStorage.setItem("module", "ipcollector");
                    history.push("/ednipamdashboard");
                  }}
                >
                  IP Collector
                </StyledMenuItem>
                <StyledMenuItem
                  key="ipam"
                  onClick={() => {
                    setModule("ipam");
                    localStorage.setItem("module", "ipam");
                    history.push("/arp");
                  }}
                >
                  IPAM
                </StyledMenuItem>
                <StyledMenuItem
                  key="ednexchanges"
                  onClick={() => {
                    setModule("ednexchanges");
                    localStorage.setItem("module", "ednexchanges");
                    history.push("/ednexchangedashboard");
                  }}
                >
                  EDN Exchange
                </StyledMenuItem>
                <StyledMenuItem
                  key="cybersecuritymodule"
                  onClick={() => {
                    setModule("cybersecuritymodule");
                    localStorage.setItem("module", "cybersecuritymodule");
                    history.push("/ednvulnerabilitydashboard");
                  }}
                >
                  Cyber Security
                </StyledMenuItem>
                <StyledMenuItem
                  key="f5"
                  onClick={() => {
                    setModule("f5");
                    localStorage.setItem("module", "f5");
                    console.log("edn sm tag ===>");
                    console.log(user, roles);
                    history.push("/f5dashboard");
                  }}
                >
                  F5
                </StyledMenuItem>
              </>
            ) : null}

            {user?.user_role === roles.ednSM ? (
              <>
                <StyledMenuItem
                  key="physicalmapping"
                  onClick={() => {
                    setModule("physicalmapping");
                    localStorage.setItem("module", "physicalmapping");
                    history.push("/");
                  }}
                >
                  EDN
                </StyledMenuItem>
                <StyledMenuItem key="igwsm">IGW</StyledMenuItem>
              </>
            ) : null}

            {user?.user_role !== roles.ednSM ? (
              <>
                <StyledMenuItem
                  key="ipt"
                  onClick={() => {
                    setModule("ipt");
                    localStorage.setItem("module", "ipt");
                    history.push("/iptdashboard");
                  }}
                >
                  IPT Endpoints
                </StyledMenuItem>
                <StyledMenuItem
                  key="accesspointsmodule"
                  onClick={() => {
                    setModule("accesspointsmodule");
                    localStorage.setItem("module", "accesspointsmodule");
                    history.push("/accesspoints");
                  }}
                >
                  Access Points
                </StyledMenuItem>
                {user?.user_role === roles.admin ? (
                  <StyledMenuItem
                    key="admin"
                    onClick={() => {
                      setModule("admin");
                      localStorage.setItem("module", "admin");
                      history.push("/addmember");
                    }}
                  >
                    Admin
                  </StyledMenuItem>
                ) : null}
              </>
            ) : null}
          </StyledMenu>
        </div>
        <NavIcons setShowCPModal={setShowCPModal} />
      </StyledBar>
      <StyledBar />

      <Row>
        <StyledMenuColumn
          xs={{ span: 4 }}
          md={{ span: 4 }}
          lg={{ span: 4 }}
          xl={{ span: 4 }}
        >
          {module === "inventorymodule" ? (
            <InventoryMenu
              user={user}
              roles={roles}
              history={history}
              location={location}
            />
          ) : null}

          {module === "cybersecuritymodule" ? (
            <CyberSecurityMenu
              user={user}
              roles={roles}
              history={history}
              location={location}
            />
          ) : null}

          {module === "accesspointsmodule" ? (
            <AccessPointsMenu
              user={user}
              roles={roles}
              history={history}
              location={location}
            />
          ) : null}

          {module === "f5" ? (
            <F5Menu
              user={user}
              roles={roles}
              history={history}
              location={location}
            />
          ) : null}

          {module === "ipt" ? (
            <IPTMenu
              user={user}
              roles={roles}
              history={history}
              location={location}
            />
          ) : null}

          {module === "dccapacity" ? (
            <DCCapacityMenu
              user={user}
              roles={roles}
              history={history}
              location={location}
            />
          ) : null}

          {module === "ipcollector" ? (
            <IPCollectorMenu
              user={user}
              roles={roles}
              history={history}
              location={location}
            />
          ) : null}

          {module === "ipam" ? (
            <IPAMMenu
              user={user}
              roles={roles}
              history={history}
              location={location}
            />
          ) : null}

          {module === "ednexchanges" ? (
            <EDNExchangesMenu
              user={user}
              roles={roles}
              history={history}
              location={location}
            />
          ) : null}

          {module === "servicemapping" ? (
            <ServiceMappingMenu
              user={user}
              roles={roles}
              history={history}
              location={location}
            />
          ) : null}

          {module === "physicalmapping" ? (
            <PhysicalMappingMenu
              user={user}
              roles={roles}
              history={history}
              location={location}
            />
          ) : null}

          {module === "admin" ? (
            <AdminMenu
              user={user}
              roles={roles}
              history={history}
              location={location}
            />
          ) : null}
        </StyledMenuColumn>

        <Col
          xs={{ span: 4 }}
          md={{ span: 4 }}
          lg={{ span: 4 }}
          xl={{ span: 4 }}
        ></Col>

        <StyledBodyCol
          xs={{ span: 20 }}
          md={{ span: 20 }}
          lg={{ span: 20 }}
          xl={{ span: 20 }}
        >
          {showCPModal ? (
            <CPModal
              showCPModal={showCPModal}
              setShowCPModal={setShowCPModal}
            />
          ) : null}

          <InventoryRoutes user={user} roles={roles} />
          <CyberSecurityRoutes user={user} roles={roles} />
          <PhysicalMappingRoutes user={user} roles={roles} />
          <AdminRoutes user={user} roles={roles} />
          <AccessPointsRoutes user={user} roles={roles} />
          <DCCapacityRoutes user={user} roles={roles} />
          <EDNExchangesRoutes user={user} roles={roles} />
          <ServiceMappingRoutes user={user} roles={roles} />
          <F5Routes user={user} roles={roles} />
          <IPCollectorRoutes user={user} roles={roles} />
          <IPAMRoutes user={user} roles={roles} />
          <IPTRoutes user={user} roles={roles} />
        </StyledBodyCol>
      </Row>
    </>
  );
};

export default Index;
