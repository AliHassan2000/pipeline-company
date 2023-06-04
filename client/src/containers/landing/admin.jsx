import React, { useEffect, useState } from "react";
import { Route } from "react-router-dom";
import { DatabaseOutlined, WalletOutlined } from "@ant-design/icons";
import AddMember from "../adminModule/users";
import UpdateIDIP from "../adminModule/updateIDIP";
import BulkUpdateMultipleColumns from "../adminModule/bulkUpdateMultipleColumns";
import BulkUpdateSingleColumn from "../adminModule/bulkUpdateSingleColumn";
import DeleteDeviceInSeed from "../adminModule/deleteDeviceInSeed";
import EDNIPAMFailedDevices from "../adminModule/failedDevices/ipam/edn";
import IGWIPAMFailedDevices from "../adminModule/failedDevices/ipam/igw";
import AccessPointsFailedDevices from "../adminModule/failedDevices/accessPoints";
import EDNDCCapacityFailedDevices from "../adminModule/failedDevices/dcCapacity/edn";
import IGWDCCapacityFailedDevices from "../adminModule/failedDevices/dcCapacity/igw";
import EDNExchangeFailedDevices from "../adminModule/failedDevices/ednExchange";
import InventoryFailedDevices from "../adminModule/failedDevices/inventory";
import IPTEndpointsFailedDevices from "../adminModule/failedDevices/iptEndpoints";
// import EDNPhysicalMappingFailedDevices from "../adminModule/failedDevices/physicalMapping/edn";
// import IGWPhysicalMappingFailedDevices from "../adminModule/failedDevices/physicalMapping/igw";
import EDNPhysicalMappingCDPLegacyFailedDevices from "../adminModule/failedDevices/physicalMapping/edn/cdpLegacy";
import EDNPhysicalMappingLLDPFailedDevices from "../adminModule/failedDevices/physicalMapping/edn/lldp";

import EDNServiceMappingFirewallARPFailedDevices from "../adminModule/failedDevices/serviceMapping/edn/firewallARP";
import EDNServiceMappingMACFailedDevices from "../adminModule/failedDevices/serviceMapping/edn/mac";

import IGWPhysicalMappingCDPLegacyFailedDevices from "../adminModule/failedDevices/physicalMapping/igw/cdpLegacy";
import IGWPhysicalMappingLLDPFailedDevices from "../adminModule/failedDevices/physicalMapping/igw/lldp";
import IGWPhysicalMappingMACFailedDevices from "../adminModule/failedDevices/physicalMapping/igw/mac";
import F5FailedDevices from "../adminModule/failedDevices/f5";
import {
  StyledSubMenu,
  StyledMenuItem,
  StyledMenu,
} from "../landing/styles/main.styles";

export const AdminMenu = ({ user, roles, history, location }) => {
  return (
    <>
      <StyledMenu
        user={user?.user_role}
        defaultSelectedKeys={["/"]}
        selectedKeys={[`/${location.pathname.split("/")[1]}`]}
        mode="inline"
        inlineCollapsed={false}
      >
        {user?.user_role === roles.admin ? (
          <StyledMenuItem
            style={{ marginBottom: "0px" }}
            key="/addmember"
            icon={<WalletOutlined />}
            onClick={() => history.push("/addmember")}
          >
            Users
          </StyledMenuItem>
        ) : null}

        <StyledSubMenu
          style={{ color: "white" }}
          key="updatePanels"
          icon={<DatabaseOutlined />}
          title="Update Panels"
        >
          {user?.user_role === roles.admin ? (
            <>
              <StyledMenuItem
                key="/updateidip"
                icon={<WalletOutlined />}
                onClick={() => history.push("/updateidip")}
              >
                Update ID/IP
              </StyledMenuItem>
              <StyledMenuItem
                key="/bulkupdatemultiplecolumns"
                icon={<WalletOutlined />}
                onClick={() => history.push("/bulkupdatemultiplecolumns")}
              >
                Bulk Update Multiple Columns
              </StyledMenuItem>
              <StyledMenuItem
                key="/bulkupdatesinglecolumn"
                icon={<WalletOutlined />}
                onClick={() => history.push("/bulkupdatesinglecolumn")}
              >
                Bulk Update Single Column
              </StyledMenuItem>

              <StyledMenuItem
                key="/deletedeviceinseed"
                icon={<WalletOutlined />}
                onClick={() => history.push("/deletedeviceinseed")}
              >
                Delete Device in Seed
              </StyledMenuItem>
            </>
          ) : null}
        </StyledSubMenu>
        {user?.user_role === roles.admin ? (
          <StyledSubMenu
            style={{ color: "white", paddingBottom: "200px" }}
            key="faileddevices"
            icon={<DatabaseOutlined />}
            title="Failed Devices"
          >
            <StyledSubMenu
              style={{ color: "white" }}
              key="inventoryfaileddevices"
              icon={<DatabaseOutlined />}
              title="Inventory"
            >
              <StyledMenuItem
                key="/inventoryfaileddevices"
                icon={<WalletOutlined />}
                onClick={() => history.push("/inventoryfaileddevices")}
              >
                Inventory
              </StyledMenuItem>
            </StyledSubMenu>
            <StyledSubMenu
              style={{ color: "white" }}
              key="dccapacityfaileddevices"
              icon={<DatabaseOutlined />}
              title="DC Capacity"
            >
              <StyledMenuItem
                key="/edndccapacityfaileddevices"
                icon={<WalletOutlined />}
                onClick={() => history.push("/edndccapacityfaileddevices")}
              >
                EDN
              </StyledMenuItem>
              <StyledMenuItem
                key="/igwdccapacityfaileddevices"
                icon={<WalletOutlined />}
                onClick={() => history.push("/igwdccapacityfaileddevices")}
              >
                IGW
              </StyledMenuItem>
            </StyledSubMenu>
            <StyledSubMenu
              style={{ color: "white" }}
              key="ipamfaileddevices"
              icon={<DatabaseOutlined />}
              title="IP Collector"
            >
              <StyledMenuItem
                key="/ednipamfaileddevices"
                icon={<WalletOutlined />}
                onClick={() => history.push("/ednipamfaileddevices")}
              >
                EDN
              </StyledMenuItem>
              <StyledMenuItem
                key="/igwipamfaileddevices"
                icon={<WalletOutlined />}
                onClick={() => history.push("/igwipamfaileddevices")}
              >
                IGW
              </StyledMenuItem>
            </StyledSubMenu>
            <StyledSubMenu
              style={{ color: "white" }}
              key="ednexchangefaileddevices"
              icon={<DatabaseOutlined />}
              title="EDN Exchange"
            >
              <StyledMenuItem
                key="/ednexchangefaileddevices"
                icon={<WalletOutlined />}
                onClick={() => history.push("/ednexchangefaileddevices")}
              >
                EDN Exchange
              </StyledMenuItem>
            </StyledSubMenu>
            <StyledSubMenu
              style={{ color: "white" }}
              key="physicalmappingfaileddevices"
              icon={<DatabaseOutlined />}
              title="Physical Mapping"
            >
              {/* <StyledMenuItem
              key="/ednphysicalmappingfaileddevices"
              icon={<WalletOutlined />}
              onClick={() => history.push("/ednphysicalmappingfaileddevices")}
            >
              EDN
            </StyledMenuItem> */}
              <StyledSubMenu
                style={{ color: "white" }}
                key="ednphysicalmappingfaileddevices"
                icon={<DatabaseOutlined />}
                title="EDN"
              >
                <StyledMenuItem
                  key="/ednphysicalmappingcdplegacyfaileddevices"
                  icon={<WalletOutlined />}
                  onClick={() =>
                    history.push("/ednphysicalmappingcdplegacyfaileddevices")
                  }
                >
                  CDP Legacy
                </StyledMenuItem>
                <StyledMenuItem
                  key="/ednphysicalmappinglldpfaileddevices"
                  icon={<WalletOutlined />}
                  onClick={() =>
                    history.push("/ednphysicalmappinglldpfaileddevices")
                  }
                >
                  LLDP
                </StyledMenuItem>
              </StyledSubMenu>

              {/* <StyledMenuItem
              key="/igwphysicalmappingfaileddevices"
              icon={<WalletOutlined />}
              onClick={() => history.push("/igwphysicalmappingfaileddevices")}
            >
              IGW
            </StyledMenuItem> */}
              <StyledSubMenu
                style={{ color: "white" }}
                key="igwphysicalmappingfaileddevices"
                icon={<DatabaseOutlined />}
                title="IGW"
              >
                <StyledMenuItem
                  key="/igwphysicalmappingcdplegacyfaileddevices"
                  icon={<WalletOutlined />}
                  onClick={() =>
                    history.push("/igwphysicalmappingcdplegacyfaileddevices")
                  }
                >
                  CDP Legacy
                </StyledMenuItem>
                <StyledMenuItem
                  key="/igwphysicalmappinglldpfaileddevices"
                  icon={<WalletOutlined />}
                  onClick={() =>
                    history.push("/igwphysicalmappinglldpfaileddevices")
                  }
                >
                  LLDP
                </StyledMenuItem>
                <StyledMenuItem
                  key="/igwphysicalmappingmacfaileddevices"
                  icon={<WalletOutlined />}
                  onClick={() =>
                    history.push("/igwphysicalmappingmacfaileddevices")
                  }
                >
                  MAC
                </StyledMenuItem>
              </StyledSubMenu>
            </StyledSubMenu>
            {/* //////////////////////////////////////////////// */}
            <StyledSubMenu
              style={{ color: "white" }}
              key="servicemappingfaileddevices"
              icon={<DatabaseOutlined />}
              title="Service Mapping"
            >
              <StyledSubMenu
                style={{ color: "white" }}
                key="ednservicemappingfaileddevices"
                icon={<DatabaseOutlined />}
                title="EDN"
              >
                <StyledMenuItem
                  key="/ednservicemappingfirewallarpfaileddevices"
                  icon={<WalletOutlined />}
                  onClick={() =>
                    history.push("/ednservicemappingfirewallarpfaileddevices")
                  }
                >
                  Firewall ARP
                </StyledMenuItem>
                <StyledMenuItem
                  key="/ednservicemappingmacfaileddevices"
                  icon={<WalletOutlined />}
                  onClick={() =>
                    history.push("/ednservicemappingmacfaileddevices")
                  }
                >
                  MAC
                </StyledMenuItem>
              </StyledSubMenu>
              <StyledSubMenu
                style={{ color: "white" }}
                key="igwservicemappingfaileddevices"
                icon={<DatabaseOutlined />}
                title="IGW"
              ></StyledSubMenu>
            </StyledSubMenu>
            {/* //////////////////////////////////////////////// */}
            <StyledSubMenu
              style={{ color: "white" }}
              key="iptendpointsfaileddevices"
              icon={<DatabaseOutlined />}
              title="IPT Endpoints"
            >
              <StyledMenuItem
                key="/iptendpointsfaileddevices"
                icon={<WalletOutlined />}
                onClick={() => history.push("/iptendpointsfaileddevices")}
              >
                IPT Endpoints
              </StyledMenuItem>
            </StyledSubMenu>
            <StyledSubMenu
              style={{ color: "white" }}
              key="f5faileddevices"
              icon={<DatabaseOutlined />}
              title="F5"
            >
              <StyledMenuItem
                key="/f5faileddevices"
                icon={<WalletOutlined />}
                onClick={() => history.push("/f5faileddevices")}
              >
                F5
              </StyledMenuItem>
            </StyledSubMenu>
            <StyledSubMenu
              style={{ color: "white" }}
              key="accesspointsfaileddevices"
              icon={<DatabaseOutlined />}
              title="Access Points"
            >
              <StyledMenuItem
                key="/accesspointsfaileddevices"
                icon={<WalletOutlined />}
                onClick={() => history.push("/accesspointsfaileddevices")}
              >
                Access Points
              </StyledMenuItem>
            </StyledSubMenu>
          </StyledSubMenu>
        ) : null}
      </StyledMenu>
    </>
  );
};

export const AdminRoutes = ({ user, roles }) => {
  return (
    <>
      {user?.user_role === roles.admin ? (
        <>
          <Route exact path="/addmember" component={AddMember} />
          <Route exact path="/updateidip" component={UpdateIDIP} />
          <Route
            exact
            path="/bulkupdatemultiplecolumns"
            component={BulkUpdateMultipleColumns}
          />
          <Route
            exact
            path="/bulkupdatesinglecolumn"
            component={BulkUpdateSingleColumn}
          />
          <Route
            exact
            path="/deletedeviceinseed"
            component={DeleteDeviceInSeed}
          />
          <Route
            exact
            path="/ednipamfaileddevices"
            component={EDNIPAMFailedDevices}
          />
          <Route
            exact
            path="/igwipamfaileddevices"
            component={IGWIPAMFailedDevices}
          />
          <Route
            exact
            path="/accesspointsfaileddevices"
            component={AccessPointsFailedDevices}
          />
          <Route
            exact
            path="/edndccapacityfaileddevices"
            component={EDNDCCapacityFailedDevices}
          />
          <Route
            exact
            path="/igwdccapacityfaileddevices"
            component={IGWDCCapacityFailedDevices}
          />
          <Route
            exact
            path="/ednexchangefaileddevices"
            component={EDNExchangeFailedDevices}
          />
          <Route
            exact
            path="/inventoryfaileddevices"
            component={InventoryFailedDevices}
          />
          <Route
            exact
            path="/iptendpointsfaileddevices"
            component={IPTEndpointsFailedDevices}
          />
          {/* <Route
                    exact
                    path="/ednphysicalmappingfaileddevices"
                    component={EDNPhysicalMappingFailedDevices}
                  /> */}
          <Route
            exact
            path="/ednphysicalmappingcdplegacyfaileddevices"
            component={EDNPhysicalMappingCDPLegacyFailedDevices}
          />
          <Route
            exact
            path="/ednphysicalmappinglldpfaileddevices"
            component={EDNPhysicalMappingLLDPFailedDevices}
          />
          <Route
            exact
            path="/ednservicemappingfirewallarpfaileddevices"
            component={EDNServiceMappingFirewallARPFailedDevices}
          />
          <Route
            exact
            path="/ednservicemappingmacfaileddevices"
            component={EDNServiceMappingMACFailedDevices}
          />
          {/* <Route
                    exact
                    path="/igwphysicalmappingfaileddevices"
                    component={IGWPhysicalMappingFailedDevices}
                  /> */}
          <Route
            exact
            path="/igwphysicalmappingcdplegacyfaileddevices"
            component={IGWPhysicalMappingCDPLegacyFailedDevices}
          />
          <Route
            exact
            path="/igwphysicalmappinglldpfaileddevices"
            component={IGWPhysicalMappingLLDPFailedDevices}
          />
          <Route
            exact
            path="/igwphysicalmappingmacfaileddevices"
            component={IGWPhysicalMappingMACFailedDevices}
          />
          <Route exact path="/f5faileddevices" component={F5FailedDevices} />
        </>
      ) : null}
    </>
  );
};
